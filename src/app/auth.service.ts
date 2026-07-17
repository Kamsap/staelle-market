import { DOCUMENT } from "@angular/common";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Injectable, computed, inject, signal } from "@angular/core";
import { Observable, tap } from "rxjs";
import { API_CONFIG } from "./api.config";

export interface Customer {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  points: number;
}

export interface RegisterData {
  full_name: string;
  email: string;
  phone: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  customer: Customer;
}

@Injectable({ providedIn: "root" })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly storage = inject(DOCUMENT).defaultView?.localStorage;
  private readonly tokenKey = "staelle_access_token";

  readonly token = signal<string | null>(
    this.storage?.getItem(this.tokenKey) ?? null,
  );
  readonly customer = signal<Customer | null>(null);
  readonly isAuthenticated = computed(() => this.customer() !== null);

  constructor() {
    // Une session sauvegardée est vérifiée auprès du backend au rechargement de la page.
    if (this.token())
      this.refreshCustomer().subscribe({ error: () => this.logout() });
  }

  register(data: RegisterData): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_CONFIG.baseUrl}/auth/register`, data)
      .pipe(tap((response) => this.saveSession(response)));
  }

  login(data: LoginData): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_CONFIG.baseUrl}/auth/login`, data)
      .pipe(tap((response) => this.saveSession(response)));
  }

  refreshCustomer(): Observable<Customer> {
    return this.http
      .get<Customer>(`${API_CONFIG.baseUrl}/auth/me`, {
        headers: this.authHeaders(),
      })
      .pipe(tap((customer) => this.customer.set(customer)));
  }

  logout(): void {
    this.storage?.removeItem(this.tokenKey);
    this.token.set(null);
    this.customer.set(null);
  }

  authHeaders(): HttpHeaders {
    const token = this.token();
    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  private saveSession(response: AuthResponse): void {
    this.storage?.setItem(this.tokenKey, response.access_token);
    this.token.set(response.access_token);
    this.customer.set(response.customer);
  }
}
