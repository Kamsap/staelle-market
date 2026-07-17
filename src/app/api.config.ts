export interface ApiConfig {
  catalogEnabled: boolean;
  baseUrl: string;
  productsPath: string;
}

// L'API de production vit sur un sous-domaine isolé. En local et avec Docker,
// l'URL relative continue de passer par le proxy déjà configuré.
const baseUrl =
  window.location.hostname === "staelle-shop-deal.wesolve-digital.fr"
    ? "https://api.staelle.wesolve-digital.fr/api/v1"
    : "/api/v1";

export const API_CONFIG: ApiConfig = {
  catalogEnabled: false,
  baseUrl,
  productsPath: "/products",
};
