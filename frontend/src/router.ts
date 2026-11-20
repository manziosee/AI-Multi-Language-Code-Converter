import { ref } from 'vue';

/**
 * Tiny hash router — keeps the bundle dependency-free and works on any
 * static host without rewrite rules.
 *   #/                 landing page
 *   #/app/<section>    workspace section
 */
export type AppSection = 'convert' | 'batch' | 'history' | 'guides';
export type Route = { name: 'landing' } | { name: 'app'; section: AppSection };

const SECTIONS: AppSection[] = ['convert', 'batch', 'history', 'guides'];

function parse(): Route {
  const hash = window.location.hash.replace(/^#\/?/, '');
  if (hash.startsWith('app')) {
    const section = hash.split('/')[1] as AppSection;
    return { name: 'app', section: SECTIONS.includes(section) ? section : 'convert' };
  }
  return { name: 'landing' };
}

export const route = ref<Route>(parse());

window.addEventListener('hashchange', () => {
  const prev = route.value.name;
  route.value = parse();
  if (prev !== route.value.name) window.scrollTo(0, 0);
});

export function hrefFor(target: 'landing' | AppSection): string {
  return target === 'landing' ? '#/' : `#/app/${target}`;
}

export function navigate(target: 'landing' | AppSection) {
  window.location.hash = hrefFor(target);
}
