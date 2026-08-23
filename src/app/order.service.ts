import { HttpClient } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable } from "rxjs";
import { API_CONFIG } from "./api.config";
import { AuthService } from "./auth.service";
import { Product } from "./products";

interface OrderRecord {
  id: number;
  reference: string;
  customer_id: number | null;
  status: string;
}

@Injectable({ providedIn: "root" })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);

  /** Enregistre la commande sans bloquer l'ouverture de WhatsApp. */
  trackOrder(product: Product, reference: string): Observable<OrderRecord> {
    return this.http.post<OrderRecord>(
      `${API_CONFIG.baseUrl}/orders`,
      {
        reference,
        product_id: product.id,
      },
      { headers: this.auth.authHeaders() },
    );
  }
}
