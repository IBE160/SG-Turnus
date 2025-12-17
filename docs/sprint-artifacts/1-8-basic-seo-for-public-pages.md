### Story 1.8: Basic SEO for Public Pages

As a marketing team member,
I want basic SEO to be applied to the landing page,
So that potential users can discover the tool through search engines.

**Acceptance Criteria:**

**Given** the public-facing landing page
**When** the page is deployed
**Then** it has a relevant `<title>` tag.
**And** it has a descriptive meta description.
**And** it has appropriate header tags (`<h1>`, `<h2>`, etc.).

**Prerequisites:** Story 1.1

**Technical Notes:** Covers FR26. For an SPA, Server-Side Rendering (SSR) or Static Site Generation (SSG) for public-facing pages might be necessary for optimal SEO. Frameworks like Next.js handle this out of the box.