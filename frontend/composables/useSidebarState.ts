/**
 * SSR-safe sidebar state composable
 *
 * Uses useCookie instead of localStorage to ensure consistent
 * rendering between server and client (fixes hydration mismatch).
 */

export const useSidebarState = () => {
  const sidebarCollapsed = useCookie<boolean>('sidebar-collapsed', {
    default: () => false,
    watch: true,
  })

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    sidebarCollapsed,
    toggleSidebar,
  }
}
