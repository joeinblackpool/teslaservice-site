// Place-name normalising shared by the Worker's place search and tools/place_search.mjs (keep them in step).
export const qnorm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, ' ').trim();
