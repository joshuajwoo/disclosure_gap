import type { NextConfig } from "next";

const githubPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  output: githubPages ? "export" : "standalone",
  basePath: githubPages ? "/disclosure_gap" : undefined,
  trailingSlash: githubPages,
  poweredByHeader: false,
};

export default nextConfig;
