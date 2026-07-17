export interface ApiConfig {
  catalogEnabled: boolean;
  baseUrl: string;
  productsPath: string;
}

// URL relative volontaire :
// - en local, Angular redirige /api vers FastAPI via proxy.conf.json ;
// - en Docker, Nginx redirige /api vers le conteneur backend ;
// - en production, on garde le même code si le domaine sert le front et l'API.
export const API_CONFIG: ApiConfig = {
  catalogEnabled: false,
  baseUrl: "/api/v1",
  productsPath: "/products",
};
