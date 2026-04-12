import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@spark/ui", "@spark/core", "@spark/views"],
};

export default nextConfig;
