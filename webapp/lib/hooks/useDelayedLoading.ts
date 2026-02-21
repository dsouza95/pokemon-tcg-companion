import { useEffect, useState } from "react";

/**
 * Returns true only after `isLoading` has been true for longer than `delayMs`.
 * Prevents skeleton flashes when responses are fast.
 */
export function useDelayedLoading(isLoading: boolean, delayMs = 200): boolean {
  const [showLoading, setShowLoading] = useState(false);

  useEffect(() => {
    if (!isLoading) {
      setShowLoading(false);
      return;
    }

    const timer = setTimeout(() => setShowLoading(true), delayMs);
    return () => clearTimeout(timer);
  }, [isLoading, delayMs]);

  return showLoading;
}