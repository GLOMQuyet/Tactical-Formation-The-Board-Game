import { useCallback, useEffect, useRef, useState } from 'react';

export function useToast(): [string | null, (message: string) => void] {
  const [message, setMessage] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const show = useCallback((text: string) => {
    setMessage(text);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setMessage(null), 2200);
  }, []);
  useEffect(() => () => clearTimeout(timer.current), []);
  return [message, show];
}

export function Toast({ message }: { message: string | null }) {
  if (!message) return null;
  return <div className="toast" role="status">{message}</div>;
}
