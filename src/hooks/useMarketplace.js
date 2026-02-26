import { useEffect, useState } from 'react'

export function useMarketplace(apiBase, initialListings) {
  const [notice, setNotice] = useState('')
  const [listings, setListings] = useState(initialListings)
  const [createdPlaylist, setCreatedPlaylist] = useState(null)

  useEffect(() => {
    const loadListings = async () => {
      try {
        const response = await fetch(`${apiBase}/api/playlists`)
        if (!response.ok) return
        const data = await response.json()
        if (Array.isArray(data.listings)) {
          setListings(data.listings)
        }
      } catch (_error) {
        setNotice('Marketplace is in offline mode. Start backend for live listings.')
      }
    }

    loadListings()
  }, [apiBase])

  const handleCreatePlaylist = (event, onCreated) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)

    const draft = {
      name: form.get('name')?.toString().trim(),
      creator: form.get('creator')?.toString().trim(),
      genre: form.get('genre')?.toString().trim(),
      cover: form.get('cover')?.toString().trim(),
    }

    if (!draft.name || !draft.creator || !draft.genre || !draft.cover) {
      return
    }

    setCreatedPlaylist(draft)
    setNotice('Playlist created. Open Store to set a price and list it.')
    onCreated?.()
    event.currentTarget.reset()
  }

  const handleSellPlaylist = async (event) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const price = Number(form.get('price'))

    if (!createdPlaylist || price <= 0) {
      return
    }

    const payload = {
      ...createdPlaylist,
      price,
    }

    try {
      const response = await fetch(`${apiBase}/api/playlists`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error('Create failed')
      const data = await response.json()
      setListings((prev) => [data.listing, ...prev])
      setNotice('Playlist listed successfully.')
      setCreatedPlaylist(null)
      event.currentTarget.reset()
    } catch (_error) {
      const offlineListing = { id: Date.now(), ...payload }
      setListings((prev) => [offlineListing, ...prev])
      setNotice('Saved locally. Start backend to persist playlists.')
      setCreatedPlaylist(null)
      event.currentTarget.reset()
    }
  }

  return {
    notice,
    setNotice,
    listings,
    createdPlaylist,
    handleCreatePlaylist,
    handleSellPlaylist,
  }
}
