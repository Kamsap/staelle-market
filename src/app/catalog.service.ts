import { HttpClient } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable, catchError, map, of } from "rxjs";
import { API_CONFIG } from "./api.config";
import { Product, PRODUCTS } from "./products";

interface ProductCollectionResponse {
  items: Product[];
}

type ProductApiResponse = Product[] | ProductCollectionResponse;

@Injectable({ providedIn: "root" })
export class CatalogService {
  private readonly http = inject(HttpClient);

  getProducts(): Observable<Product[]> {
    if (!API_CONFIG.catalogEnabled) return of(PRODUCTS);

    return this.http
      .get<ProductApiResponse>(
        `${API_CONFIG.baseUrl}${API_CONFIG.productsPath}`,
      )
      .pipe(
        map((response) =>
          Array.isArray(response) ? response : response.items,
        ),
        map((products) => products.map((item) => this.normalizeProduct(item))),
        catchError(() => of(PRODUCTS)),
      );
  }

  private normalizeProduct(item: Product): Product {
    const images = item.images?.length ? item.images : [item.image];
    return { ...item, image: item.image || images[0], images };
  }
}
