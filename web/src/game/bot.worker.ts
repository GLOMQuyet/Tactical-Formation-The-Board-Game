// Runs one bot search per message, off the page's main thread.

import { searchHere, type SearchJob } from './search';

const scope = self as unknown as {
  onmessage: ((event: MessageEvent<SearchJob>) => void) | null;
  postMessage(message: unknown): void;
};

scope.onmessage = (event) => {
  scope.postMessage({ id: event.data.id, move: searchHere(event.data) });
};
