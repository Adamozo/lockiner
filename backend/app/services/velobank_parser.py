"""VeloBank PDF bank statement parser — text-based extraction."""

import io
import re
from datetime import datetime
from typing import Optional

import pdfplumber


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Transaction first-line starts with two dates: YYYY.MM.DD YYYY.MM.DD
_LINE_START_RE = re.compile(
    r'^(\d{4}\.\d{2}\.\d{2})\s+'   # booking date
    r'(\d{4}\.\d{2}\.\d{2})\s+'    # transaction date
    r'(.+)$'                         # rest of line
)

# Amount + balance at the end of the first line.
# Amounts use Polish format: comma as decimal separator, space as thousands.
# E.g.: "-79,62 155,07" or "1 200,00 1 228,23"
_AMOUNT_NUM = r'-?\d{1,3}(?:\s\d{3})*,\d{2}'
_BALANCE_NUM = r'\d{1,3}(?:\s\d{3})*,\d{2}'
_AMOUNTS_RE = re.compile(
    r'(' + _AMOUNT_NUM + r')\s+(' + _BALANCE_NUM + r')\s*$'
)

# Lines to skip (summaries, headers)
_SKIP_RE = re.compile(
    r'^(Saldo\s+pocz[aą]tkowe|Data\s+ksi[eę]gowania|Data\s+transakcji'
    r'|Opis\s+transakcji|Kwota\s+transakcji|Infolinia|VeloBank\s+S\.A)',
    re.IGNORECASE,
)

# When these appear, all transactions are done — ignore everything after
_FOOTER_START_RE = re.compile(
    r'^(Obroty\s+WN|Obroty\s+MA|Saldo\s+ko[nń]cowe)',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Category auto-detection
# ---------------------------------------------------------------------------

_CATEGORY_RULES: list[tuple[str, str]] = [
    (r'biedronka|biedr\s*onka|jmp\s+s\.a\.|lidl|auchan|kaufland|tesco|carrefour|netto|spar|stokrotka', 'Jedzenie'),
    (r'żabka|zabka|fresh market|delikatesy|sevi kebab|kebab|mcdonalds?|burger|kfc|pizza|sushi|restaur|bistro|cafe|precle?|lepione', 'Jedzenie'),
    (r'stacja paliw|paliw|bp |orlen|shell|circle k|lotos', 'Transport'),
    (r'pkp|pkm|mpk|bilet|ztm|peka|koleje|uber|bolt|taxi', 'Transport'),
    (r'apteka|farmacja|pharma|doz |dbam o zdrowie|gemini', 'Zdrowie'),
    (r'netflix|spotify|youtube|hbo|disney|canal\+|apple tv|tidal', 'Rozrywka'),
    (r'cinema|kino|teatr|muzeum', 'Rozrywka'),
    (r'empik|mediamarkt|rtv euro|komputronik|neonet', 'Elektronika'),
    (r'h&m|zara|reserved|house |mohito|pepco|dealz|sinsay|cropp', 'Odzież'),
    (r'allegro|amazon|olx|ebay', 'Zakupy Online'),
    (r'zooplus|zoo\s|pet shop|pupil|zoolog', 'Zwierzęta'),
    (r'nfm\s|galeria|pl\s+ph\s|pl\s+sbx', 'Zakupy'),
    (r'przelew przychodzący|wpłata|uznanie', 'Przychody'),
]


def _parse_amount(text: str) -> Optional[float]:
    """Parse Polish-formatted amount: '-79,62' or '1 200,00'."""
    if not text:
        return None
    cleaned = text.strip().replace('\xa0', '').replace(' ', '')
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(text: str) -> Optional[str]:
    """Convert VeloBank date (2026.02.02) to ISO (2026-02-02)."""
    try:
        return datetime.strptime(text.strip(), '%Y.%m.%d').strftime('%Y-%m-%d')
    except ValueError:
        return None


def _extract_merchant(description: str) -> str:
    """Extract clean merchant / transfer purpose from full description."""
    desc = description.strip()

    # Card transaction: ends description with "PLN w MERCHANT_NAME, CITY, POL"
    match = re.search(r'[Pp][Ll][Nn]\s+w\s+(.+?)(?:,\s*[A-Z]{3}\s*$|$)', desc, re.DOTALL)
    if match:
        merchant = match.group(1).strip().replace('\n', ' ')
        # Strip trailing country code like ", POL" or ", DEU"
        merchant = re.sub(r',\s*[A-Z]{2,3}\s*$', '', merchant).strip()
        return merchant

    # Transfer: extract sender + title
    purpose = re.search(r'Tytu[łl]em:\s*(.+?)(?:\s*$)', desc, re.IGNORECASE | re.DOTALL)
    sender = re.search(r'Prowadzonego na rzecz:\s*(.+?)(?:\s*Tytu[łl]em:|$)', desc, re.IGNORECASE | re.DOTALL)

    if purpose and sender:
        s = sender.group(1).strip().replace('\n', ' ')
        p = purpose.group(1).strip().replace('\n', ' ')
        return f"{s} – {p}"
    if purpose:
        return purpose.group(1).strip().replace('\n', ' ')

    return desc.replace('\n', ' ')


def _determine_payment_method(description: str) -> str:
    desc = description.lower()
    if 'operacja kartą' in desc or 'kartą' in desc:
        return 'card'
    if 'przelew' in desc:
        return 'transfer'
    if 'blik' in desc:
        return 'blik'
    if 'wypłata' in desc or 'bankomat' in desc or 'atm' in desc:
        return 'cash'
    return 'other'


def _categorize(description: str, amount: float) -> str:
    if amount > 0:
        return 'Przychody'
    desc_lower = description.lower()
    for pattern, category in _CATEGORY_RULES:
        if re.search(pattern, desc_lower, re.IGNORECASE):
            return category
    return 'Inne'


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_velobank_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Parse a VeloBank PDF bank statement using text extraction.

    Returns a list of dicts with keys:
        transaction_date, booking_date, description, merchant,
        amount, balance, payment_method, category
    """
    # 1. Collect all lines from all pages
    all_lines: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.splitlines())

    # 2. Group lines into transaction blocks.
    #    A new block starts when a line begins with two dates.
    #    Footer lines (Obroty WN/MA, Saldo końcowe) terminate collection entirely.
    blocks: list[list[str]] = []
    current: list[str] = []
    in_footer = False

    for line in all_lines:
        line = line.strip()
        if not line:
            continue
        if _FOOTER_START_RE.match(line):
            in_footer = True
            if current:
                blocks.append(current)
                current = []
            continue
        if in_footer:
            continue
        if _SKIP_RE.match(line):
            continue
        if _LINE_START_RE.match(line):
            if current:
                blocks.append(current)
            current = [line]
        else:
            if current:
                current.append(line)
            # else: header lines before first transaction — skip

    if current:
        blocks.append(current)

    # 3. Parse each block
    transactions: list[dict] = []

    for block in blocks:
        first_line = block[0]
        m = _LINE_START_RE.match(first_line)
        if not m:
            continue

        booking_date = _parse_date(m.group(1))
        transaction_date = _parse_date(m.group(2))
        rest = m.group(3)  # everything after the two dates on the first line

        if not booking_date:
            continue

        # Extract amount + balance from the END of the first line
        am = _AMOUNTS_RE.search(rest)
        if not am:
            continue

        amount = _parse_amount(am.group(1))
        balance = _parse_amount(am.group(2))
        if amount is None:
            continue

        # Description = first-line prefix (before amount) + continuation lines
        desc_start = rest[:am.start()].strip()
        continuation = ' '.join(block[1:]).strip()
        full_description = (desc_start + ' ' + continuation).strip()

        merchant = _extract_merchant(full_description)
        payment_method = _determine_payment_method(full_description)
        category = _categorize(full_description, amount)

        transactions.append({
            'transaction_date': transaction_date or booking_date,
            'booking_date': booking_date,
            'description': full_description,
            'merchant': merchant,
            'amount': amount,
            'balance': balance,
            'payment_method': payment_method,
            'category': category,
        })

    return transactions
