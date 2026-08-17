import { HttpClient } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable } from "rxjs";
import { API_CONFIG } from "../api.config";

export interface AdminUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

export interface AdminDashboard {
  active_products: number;
  total_available_stock: number;
  low_stock_variants: number;
  pending_orders: number;
  confirmed_revenue: number;
}

export interface AdminProductVariant {
  id?: number;
  sku: string;
  size: string | null;
  color: string | null;
  selling_price: number;
  compare_at_price: number | null;
  cost_price: number | null;
  stock_on_hand: number;
  stock_reserved: number;
  low_stock_threshold: number;
  is_active: boolean;
  available_stock?: number;
}

export interface AdminProductImage {
  id?: number;
  path: string;
  alt_text: string;
  position: number;
}

export interface AdminProductPayload {
  name: string;
  slug: string;
  brand: string;
  category: string;
  description: string;
  status: "draft" | "active" | "archived";
  featured: boolean;
  variants: AdminProductVariant[];
  images: AdminProductImage[];
}

export interface AdminProduct extends AdminProductPayload {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface StockAdjustmentPayload {
  variant_id: number;
  quantity_delta: number;
  kind: "receipt" | "sale" | "return" | "correction" | "damaged";
  note: string;
}

@Injectable({ providedIn: "root" })
export class AdminService {
  private readonly http = inject(HttpClient);
  private readonly options = { withCredentials: true } as const;

  session(): Observable<AdminUser> {
    return this.http.get<AdminUser>(`${API_CONFIG.baseUrl}/admin/auth/me`, this.options);
  }

  login(email: string, password: string): Observable<AdminUser> {
    return this.http.post<AdminUser>(
      `${API_CONFIG.baseUrl}/admin/auth/login`,
      { email, password },
      this.options,
    );
  }

  logout(): Observable<void> {
    return this.http.post<void>(`${API_CONFIG.baseUrl}/admin/auth/logout`, {}, this.options);
  }

  dashboard(): Observable<AdminDashboard> {
    return this.http.get<AdminDashboard>(`${API_CONFIG.baseUrl}/admin/dashboard`, this.options);
  }

  products(): Observable<AdminProduct[]> {
    return this.http.get<AdminProduct[]>(`${API_CONFIG.baseUrl}/admin/products`, this.options);
  }

  createProduct(payload: AdminProductPayload): Observable<AdminProduct> {
    return this.http.post<AdminProduct>(
      `${API_CONFIG.baseUrl}/admin/products`,
      payload,
      this.options,
    );
  }

  updateProduct(id: number, payload: AdminProductPayload): Observable<AdminProduct> {
    return this.http.put<AdminProduct>(
      `${API_CONFIG.baseUrl}/admin/products/${id}`,
      payload,
      this.options,
    );
  }

  archiveProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${API_CONFIG.baseUrl}/admin/products/${id}`, this.options);
  }

  adjustStock(payload: StockAdjustmentPayload): Observable<unknown> {
    return this.http.post(
      `${API_CONFIG.baseUrl}/admin/stock-adjustments`,
      payload,
      this.options,
    );
  }

  uploadImage(file: File): Observable<{ url: string }> {
    const form = new FormData();
    form.append("file", file);
    return this.http.post<{ url: string }>(
      `${API_CONFIG.baseUrl}/admin/uploads`,
      form,
      this.options,
    );
  }
}
