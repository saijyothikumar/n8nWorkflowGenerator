import { RenderMode, ServerRoute } from '@angular/ssr';

// Define the root path so the server router recognizes it during build.
// Use RenderMode.Disabled to avoid prerendering at build time.
export const serverRoutes: ServerRoute[] = [
	{ path: '', renderMode: RenderMode.Server }
];
