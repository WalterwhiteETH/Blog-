import { useEffect, useMemo, useRef, useState } from 'react'

export function usePlayer(tracks) {
  const audioRef = useRef(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)

  const currentTrack = useMemo(() => tracks[currentIndex], [tracks, currentIndex])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const onLoadedMetadata = () => setDuration(audio.duration || 0)
    const onTimeUpdate = () => setProgress(audio.currentTime || 0)
    const onEnded = () => setCurrentIndex((prev) => (prev + 1) % tracks.length)

    audio.addEventListener('loadedmetadata', onLoadedMetadata)
    audio.addEventListener('timeupdate', onTimeUpdate)
    audio.addEventListener('ended', onEnded)

    return () => {
      audio.removeEventListener('loadedmetadata', onLoadedMetadata)
      audio.removeEventListener('timeupdate', onTimeUpdate)
      audio.removeEventListener('ended', onEnded)
    }
  }, [tracks.length])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !currentTrack) return

    audio.src = currentTrack.audio
    audio.load()
    setProgress(0)

    if (isPlaying) {
      audio.play().catch(() => setIsPlaying(false))
    }
  }, [currentTrack, isPlaying])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
      return
    }

    audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
  }

  const skipTrack = (direction) => {
    setCurrentIndex((prev) => {
      if (direction === 'next') return (prev + 1) % tracks.length
      return (prev - 1 + tracks.length) % tracks.length
    })
  }

  const handleSeek = (event) => {
    const value = Number(event.target.value)
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = value
    setProgress(value)
  }

  return {
    audioRef,
    currentTrack,
    currentIndex,
    isPlaying,
    progress,
    duration,
    setCurrentIndex,
    togglePlay,
    skipTrack,
    handleSeek,
  }
}
