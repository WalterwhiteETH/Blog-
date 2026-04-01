import express from 'express'
import cors from 'cors'
import Stripe from 'stripe'
import dotenv from 'dotenv'

dotenv.config()

const app = express()
const port = process.env.PORT || 8787
const clientUrl = process.env.CLIENT_URL || 'http://localhost:5173'
const stripeSecret = process.env.STRIPE_SECRET_KEY
const stripe = stripeSecret ? new Stripe(stripeSecret) : null

app.use(cors({ origin: clientUrl }))
app.use(express.json())

let listings = [
  {
    id: 1,
    name: 'Lo-fi Focus Pack',
    creator: 'Nora',
    genre: 'Lo-fi',
    price: 8,
    cover:
      'https://images.unsplash.com/photo-1461784180009-21121b2f204c?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 2,
    name: 'Afrobeats Party Mix',
    creator: 'Kane',
    genre: 'Afrobeats',
    price: 12,
    cover:
      'https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=800&q=80',
  },
]

app.get('/api/health', (_req, res) => {
  res.json({ ok: true })
})

app.get('/api/playlists', (_req, res) => {
  res.json({ listings })
})

app.post('/api/playlists', (req, res) => {
  const { name, creator, genre, price, cover } = req.body

  if (!name || !creator || !genre || !cover || !Number.isFinite(Number(price)) || Number(price) <= 0) {
    return res.status(400).json({ error: 'Invalid payload' })
  }

  const listing = {
    id: Date.now(),
    name: String(name).trim(),
    creator: String(creator).trim(),
    genre: String(genre).trim(),
    price: Number(price),
    cover: String(cover).trim(),
  }

  listings = [listing, ...listings]
  return res.status(201).json({ listing })
})

app.post('/api/checkout-session', async (req, res) => {
  const { playlistId } = req.body
  const listing = listings.find((item) => item.id === Number(playlistId))

  if (!listing) {
    return res.status(404).json({ error: 'Playlist not found' })
  }

  if (!stripe) {
    return res.json({
      demo: true,
      message:
        'Stripe is not configured yet. Add STRIPE_SECRET_KEY to enable real checkout.',
    })
  }

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [
        {
          quantity: 1,
          price_data: {
            currency: 'usd',
            unit_amount: Math.round(listing.price * 100),
            product_data: {
              name: listing.name,
              description: `Playlist by ${listing.creator}`,
            },
          },
        },
      ],
      success_url: `${clientUrl}/?payment=success`,
      cancel_url: `${clientUrl}/?payment=cancelled`,
    })

    return res.json({ checkoutUrl: session.url })
  } catch (_error) {
    return res.status(500).json({ error: 'Failed to create checkout session' })
  }
})

app.listen(port, () => {
  console.log(`API server listening on http://localhost:${port}`)
})