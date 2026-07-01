// Deterministic placeholder gradient per movie/person id — stands in for a
// precomputed "dominant color" until the real poster image loads.
const PALETTE = [
  ["#7a5a2e", "#2a1e12"],
  ["#4a3316", "#0e0a06"],
  ["#4a181a", "#0d0708"],
  ["#8a4416", "#12222c"],
  ["#1a3a54", "#05080d"],
  ["#2e4030", "#0c110c"],
  ["#2a4444", "#0a1010"],
  ["#2e2860", "#3a1a3a"],
  ["#6a1616", "#140606"],
  ["#1a3646", "#080d12"],
  ["#42285e", "#12202a"],
  ["#26343f", "#0a0e12"],
];

export function gradientFor(id) {
  const [a, b] = PALETTE[Math.abs(id) % PALETTE.length];
  return `linear-gradient(155deg, ${a} 0%, ${b} 72%)`;
}
