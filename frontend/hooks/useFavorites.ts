"use client";

import { useState, useEffect, useCallback } from "react";

const FAVORITES_KEY = "mockupai_favorite_scenes";

export function useFavorites() {
  const [favorites, setFavorites] = useState<string[]>([]);

  // Load favorites from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(FAVORITES_KEY);
      if (stored) {
        try {
          setFavorites(JSON.parse(stored));
        } catch {
          setFavorites([]);
        }
      }
    }
  }, []);

  // Save to localStorage whenever favorites change
  const saveFavorites = useCallback((newFavorites: string[]) => {
    setFavorites(newFavorites);
    if (typeof window !== "undefined") {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(newFavorites));
    }
  }, []);

  const addFavorite = useCallback(
    (sceneId: string) => {
      if (!favorites.includes(sceneId)) {
        saveFavorites([...favorites, sceneId]);
      }
    },
    [favorites, saveFavorites]
  );

  const removeFavorite = useCallback(
    (sceneId: string) => {
      saveFavorites(favorites.filter((id) => id !== sceneId));
    },
    [favorites, saveFavorites]
  );

  const toggleFavorite = useCallback(
    (sceneId: string) => {
      if (favorites.includes(sceneId)) {
        removeFavorite(sceneId);
      } else {
        addFavorite(sceneId);
      }
    },
    [favorites, addFavorite, removeFavorite]
  );

  const isFavorite = useCallback(
    (sceneId: string) => favorites.includes(sceneId),
    [favorites]
  );

  return {
    favorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
  };
}
