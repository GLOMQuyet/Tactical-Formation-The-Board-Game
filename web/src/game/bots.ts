// Bot searches run in a Web Worker so the board keeps animating while a bot
// thinks (as ai/worker.py does on the desktop). Where workers are not
// available the search runs on the page instead.

import { ON_PAGE_BUDGET, searchHere, type FoundMove, type SearchJob } from './search';

export type { FoundMove };

let worker: Worker | null = null;
let broken = false;
let seq = 0;
const waiting = new Map<number, (reply: { move: FoundMove } | null) => void>();

function workerFailed() {
  broken = true;
  worker?.terminate();
  worker = null;
  for (const [id, done] of waiting) {
    waiting.delete(id);
    done(null);   // searched again on the page
  }
}

function getWorker(): Worker {
  if (!worker) {
    worker = new Worker(new URL('./bot.worker.ts', import.meta.url), { type: 'module' });
    worker.onmessage = (event: MessageEvent<{ id: number; move: FoundMove }>) => {
      const done = waiting.get(event.data.id);
      waiting.delete(event.data.id);
      done?.({ move: event.data.move });
    };
    worker.onerror = workerFailed;
  }
  return worker;
}

/** The bot's move for the position in `job`. */
export function searchMove(job: Omit<SearchJob, 'id'>): Promise<FoundMove> {
  const full: SearchJob = { ...job, id: ++seq };
  return new Promise((resolve) => {
    const here = () => setTimeout(() => resolve(searchHere(full, ON_PAGE_BUDGET)), 30);
    if (!broken) {
      try {
        const w = getWorker();
        waiting.set(full.id, (reply) => (reply ? resolve(reply.move) : here()));
        w.postMessage(full);
        return;
      } catch {
        broken = true;
      }
    }
    here();
  });
}

/** Stop any running search; its promise never settles. */
export function cancelSearches(): void {
  if (waiting.size && worker) {
    worker.terminate();
    worker = null;
    waiting.clear();
  }
}
