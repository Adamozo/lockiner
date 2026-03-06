"""Bank Millennium PDF bank statement parser."""

import io
import re
from datetime import datetime
from typing import Optional

import pdfplumber


# ---------------------------------------------------------------------------
# Amount parsing — Millennium uses dot as thousands separator, dash at END
# e.g.: "86,00-" = -86.00,  "4.999,00" = 4999.00
# ---------------------------------------------------------------------------

def _parse_amount(text: str) -> Optional[float]:
    text = text.strip()
    if not text:
        return None
    negative = text.endswith('-')
    if negative:
        text = text[:-1]
    # Remove dot (thousands separator), replace comma with dot (decimal)
    text = text.replace('.', '').replace(',', '.')
    try:
        val = float(text)
        return -val if negative else val
    except ValueError:
        return None


def _parse_date(text: str) -> Optional[str]:
    """Millennium dates are already YYYY-MM-DD."""
    text = text.strip()
    try:
        datetime.strptime(text, '%Y-%m-%d')
        return text
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Transaction first line: YYYY-MM-DD  YYYY-MM-DD  TX_TYPE  AMOUNT  BALANCE
_LINE_START_RE = re.compile(
    r'^(\d{4}-\d{2}-\d{2})\s+'
    r'(\d{4}-\d{2}-\d{2})\s+'
    r'(.+)$'
)

# Amount + balance at end of first line.
# Amounts: "86,00-" or "4.999,00" — balance never has trailing dash.
_AMOUNT_NUM = r'\d{1,3}(?:\.\d{3})*,\d{2}-?'
_BALANCE_NUM = r'\d{1,3}(?:\.\d{3})*,\d{2}'
_AMOUNTS_RE = re.compile(
    r'(' + _AMOUNT_NUM + r')\s+(' + _BALANCE_NUM + r')\s*$'
)

# Footer terminators — everything after these is irrelevant
_FOOTER_START_RE = re.compile(
    r'^(SUMAUZNA|SUMAOBC|SALDOKOŃCOWE|SALDO\s*KO[NŃ]COWE'
    r'|INFORMUJEMY|OCHRONIEGWARANCYJNEJ|DOKUMENT\s*WYGENEROWANY)',
    re.IGNORECASE,
)

# Header/boilerplate lines to skip
_SKIP_RE = re.compile(
    r'^(DATA\s*DATA|KSIĘG\.|WAL\.|OPISTRANSAKCJI|WARTOŚĆ\s*SALDO'
    r'|SALDOPOCZĄTKOWE|www\.bankmillennium|TeleMillennium'
    r'|strona\s+\d)',
    re.IGNORECASE,
)

# Continuation-line prefixes that are metadata (not merchant name)
_META_LINE_RE = re.compile(
    r'^(NaR-k:|ZR-ku:|Karta:|Dnia:|Kwotatransakcji:|ZLECENIODAWCA:|Nanrtel\.|'
    r'Na\s+R-k:|Z\s+R-ku:|Nadawca:|Odbiorca:|Tytułem:|Nanrtel\.)',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category rules (reuse same structure as VeloBank parser)
# ---------------------------------------------------------------------------

_CATEGORY_RULES: list[tuple[str, str]] = [
    (r'lidl|biedronka|auchan|kaufland|żabka|zabka|carrefour|netto|stokrotka|spar', 'Spożywcze'),
    (r'mcdonald|burger|kfc|pizza|kebab|sushi|restaur|bistro|cafe|restaumatic', 'Restauracje'),
    (r'stacja paliw|paliw|orlen|bp |shell|circle k|lotos', 'Paliwo'),
    (r'pkp|pkm|mpk|bilet|ztm|uber|bolt|taxi', 'Transport'),
    (r'apteka|farmacja|pharma|doz |dbam', 'Zdrowie'),
    (r'netflix|spotify|youtube|hbo|disney|canal\+|apple tv|tidal', 'Subskrypcje'),
    (r'zalando|empik|reserved|h&m|zara|pepco|dealz|sinsay', 'Ubrania'),
    (r'orange|play |t-mobile|tmobile|plus\s', 'Rachunki'),
    (r'tauron|pge |energa|enea|gaz |prąd|energia', 'Rachunki'),
    (r'ovh|hosting|internet|autopay', 'Rachunki'),
    (r'wspólnota|czynsz|administracja|nota\s+księ', 'Dom'),
    (r'prowizja|opłata|składka|pakiet\s+bardzo', 'Rachunki'),
    (r'wypłata|bankomat|atm', 'Inne'),
    (r'przel\.natych\.przych\.|przychodzący|uznanie|wpłata', 'Przychody'),
]


def _categorize(description: str, amount: float) -> str:
    if amount > 0:
        return 'Przychody'
    desc_lower = description.lower()
    for pattern, category in _CATEGORY_RULES:
        if re.search(pattern, desc_lower, re.IGNORECASE):
            return category
    return 'Inne'


def _determine_payment_method(tx_type_raw: str, description: str) -> str:
    tx = tx_type_raw.upper()
    desc = description.lower()
    if 'BLIKZBANKOMATU' in tx or 'WYPŁATABLIK' in tx:
        return 'cash'
    if 'BLIK' in tx:
        return 'blik'
    if 'KARTĄ' in tx or 'KARTA' in tx:
        return 'card'
    if 'PRZELEW' in tx or 'PRZEL' in tx:
        return 'transfer'
    if 'revolut' in desc:
        return 'card'
    return 'other'


def _extract_merchant(tx_type_raw: str, continuation_lines: list[str]) -> str:
    """
    Extract a clean merchant/recipient name from the transaction block.
    Strategy:
    - For card payments / BLIK: first non-metadata continuation line
    - For transfers: parse Odbiorca / Nadawca + Tytułem from the full text
    """
    full = ' '.join(continuation_lines)
    tx = tx_type_raw.upper()

    # Transfer-type: extract Odbiorca/Nadawca + Tytułem
    if 'PRZELEW' in tx or 'PRZEL' in tx:
        # Try Odbiorca
        odbiorca = re.search(r'Odbiorca:(.+?)(?:Tytu[łl]em:|NaRk:|Nanrtel\.|$)', full, re.IGNORECASE)
        nadawca = re.search(r'Nadawca:(.+?)(?:Tytu[łl]em:|$)', full, re.IGNORECASE)
        tytulem = re.search(r'Tytu[łl]em:(.+?)(?:Nanrtel\.|$)', full, re.IGNORECASE)

        parts = []
        name = (odbiorca or nadawca)
        if name:
            parts.append(name.group(1).strip())
        if tytulem:
            parts.append(tytulem.group(1).strip())
        if parts:
            return ' – '.join(parts)

    # For card / BLIK / ATM: use first meaningful continuation line
    for line in continuation_lines:
        line = line.strip()
        if not line:
            continue
        if _META_LINE_RE.match(line):
            continue
        # Skip "Karta: ...", "Dnia:...", "Kwota transakcji:..."
        if re.match(r'^(Karta:|Dnia:|Kwota)', line, re.IGNORECASE):
            continue
        return line

    return tx_type_raw


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_millennium_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Parse a Bank Millennium PDF bank statement.

    Returns list of dicts with keys:
        transaction_date, booking_date, description, merchant,
        amount, balance, payment_method, category
    """
    all_lines: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.splitlines())

    # Group into transaction blocks
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

    if current:
        blocks.append(current)

    # Parse each block
    transactions: list[dict] = []

    for block in blocks:
        m = _LINE_START_RE.match(block[0])
        if not m:
            continue

        booking_date = _parse_date(m.group(1))
        transaction_date = _parse_date(m.group(2))
        rest = m.group(3)

        if not booking_date:
            continue

        am = _AMOUNTS_RE.search(rest)
        if not am:
            continue

        amount = _parse_amount(am.group(1))
        balance = _parse_amount(am.group(2))
        if amount is None:
            continue

        tx_type_raw = rest[:am.start()].strip()
        continuation = block[1:]
        full_description = tx_type_raw + ' ' + ' '.join(continuation)

        merchant = _extract_merchant(tx_type_raw, continuation)
        payment_method = _determine_payment_method(tx_type_raw, full_description)
        category = _categorize(full_description, amount)

        transactions.append({
            'transaction_date': transaction_date or booking_date,
            'booking_date': booking_date,
            'description': full_description.strip(),
            'merchant': merchant,
            'amount': amount,
            'balance': balance,
            'payment_method': payment_method,
            'category': category,
        })

    return transactions
