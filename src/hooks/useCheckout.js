import { useState } from 'react'

export function useCheckout(apiBase, setNotice) {
  const [checkoutLoadingId, setCheckoutLoadingId] = useState(null)

  const handleCheckout = async (playlistId) => {
    setCheckoutLoadingId(playlistId)
    try {
      const response = await fetch(`${apiBase}/api/checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playlistId }),
      })
      const data = await response.json()

      if (data.checkoutUrl) {
        window.location.assign(data.checkoutUrl)
        return
      }

      setNotice(data.message || 'Checkout unavailable. Configure Stripe backend keys.')
    } catch (_error) {
      setNotice('Checkout service is offline. Start backend server.')
    } finally {
      setCheckoutLoadingId(null)
    }
  }

  return {
    checkoutLoadingId,
    handleCheckout,
  }
}
