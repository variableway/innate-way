import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@innate/ui", "@innate/core", "@innate/views"],
};

export default nextConfig;
