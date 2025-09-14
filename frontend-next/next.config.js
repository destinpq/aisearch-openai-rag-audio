/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // `appDir` was previously enabled under `experimental` for the app
  // directory. Newer Next versions may surface this as an invalid key
  // when running in certain environments. The app uses the app/ folder
  // by design; remove the experimental flag to avoid noisy warnings.
};

module.exports = nextConfig;
