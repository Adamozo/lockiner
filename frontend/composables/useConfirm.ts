interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'primary'
}

interface ConfirmState {
  open: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  variant: 'danger' | 'warning' | 'primary'
  resolve: ((value: boolean) => void) | null
}

const state = reactive<ConfirmState>({
  open: false,
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  variant: 'danger',
  resolve: null,
})

export function useConfirm() {
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      state.open = true
      state.title = options.title ?? ''
      state.message = options.message
      state.confirmText = options.confirmText ?? 'Confirm'
      state.cancelText = options.cancelText ?? 'Cancel'
      state.variant = options.variant ?? 'danger'
      state.resolve = resolve
    })
  }

  const handleConfirm = () => {
    state.open = false
    state.resolve?.(true)
    state.resolve = null
  }

  const handleCancel = () => {
    state.open = false
    state.resolve?.(false)
    state.resolve = null
  }

  return { confirm, state, handleConfirm, handleCancel }
}
