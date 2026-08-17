import { CommonModule, DOCUMENT } from "@angular/common";
import { HttpErrorResponse } from "@angular/common/http";
import { Component, OnInit, computed, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { firstValueFrom } from "rxjs";
import {
  AdminDashboard,
  AdminProduct,
  AdminProductPayload,
  AdminProductVariant,
  AdminService,
  AdminUser,
} from "./admin.service";

type ProductDraft = AdminProductPayload & { id?: number };

@Component({
  selector: "app-admin",
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: "./admin.component.html",
  styleUrl: "./admin.component.scss",
})
export class AdminComponent implements OnInit {
  private readonly api = inject(AdminService);
  private readonly document = inject(DOCUMENT);

  readonly admin = signal<AdminUser | null>(null);
  readonly dashboard = signal<AdminDashboard | null>(null);
  readonly products = signal<AdminProduct[]>([]);
  readonly draft = signal<ProductDraft | null>(null);
  readonly search = signal("");
  readonly busy = signal(false);
  readonly sessionChecked = signal(false);
  readonly feedback = signal("");
  readonly error = signal("");
  readonly uploading = signal(false);

  readonly loginEmail = signal("");
  readonly loginPassword = signal("");
  readonly stockDelta = signal(1);
  readonly stockKind = signal<"receipt" | "sale" | "return" | "correction" | "damaged">(
    "receipt",
  );
  readonly stockNote = signal("Réception de marchandise");

  readonly filteredProducts = computed(() => {
    const term = this.normalize(this.search());
    if (!term) return this.products();
    return this.products().filter((product) =>
      this.normalize(
        `${product.name} ${product.brand} ${product.category} ${product.variants.map((v) => v.sku).join(" ")}`,
      ).includes(term),
    );
  });

  ngOnInit(): void {
    this.api.session().subscribe({
      next: (admin) => {
        this.admin.set(admin);
        this.sessionChecked.set(true);
        this.refreshData();
      },
      error: () => this.sessionChecked.set(true),
    });
  }

  login(): void {
    this.clearMessages();
    this.busy.set(true);
    this.api.login(this.loginEmail(), this.loginPassword()).subscribe({
      next: (admin) => {
        this.admin.set(admin);
        this.loginPassword.set("");
        this.busy.set(false);
        this.refreshData();
      },
      error: (error) => {
        this.busy.set(false);
        this.error.set(this.errorMessage(error));
      },
    });
  }

  logout(): void {
    this.api.logout().subscribe({
      next: () => {
        this.admin.set(null);
        this.products.set([]);
        this.dashboard.set(null);
      },
      error: () => this.admin.set(null),
    });
  }

  refreshData(): void {
    // Le catalogue doit rester administrable même si un indicateur du tableau
    // de bord rencontre momentanément un problème côté serveur.
    this.api.products().subscribe({
      next: (products) => this.products.set(products),
      error: (error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) this.admin.set(null);
        else this.error.set(this.errorMessage(error));
      },
    });

    this.api.dashboard().subscribe({
      next: (dashboard) => this.dashboard.set(dashboard),
      error: (error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) this.admin.set(null);
        else
          this.error.set(
            "Le catalogue reste disponible, mais les indicateurs n’ont pas pu être chargés.",
          );
      },
    });
  }

  newProduct(): void {
    this.clearMessages();
    this.draft.set({
      name: "",
      slug: "",
      brand: "Adidas",
      category: "Sac",
      description: "",
      status: "draft",
      featured: false,
      variants: [this.emptyVariant()],
      images: [],
    });
    this.document.body.style.overflow = "hidden";
  }

  editProduct(product: AdminProduct): void {
    this.clearMessages();
    this.draft.set(JSON.parse(JSON.stringify(product)) as ProductDraft);
    this.document.body.style.overflow = "hidden";
  }

  closeEditor(): void {
    this.draft.set(null);
    this.document.body.style.overflow = "";
  }

  setName(item: ProductDraft, value: string): void {
    item.name = value;
    if (!item.id) item.slug = this.slugify(value);
  }

  addVariant(item: ProductDraft): void {
    item.variants.push(this.emptyVariant());
  }

  removeVariant(item: ProductDraft, index: number): void {
    if (item.variants.length <= 1) {
      this.error.set("Un article doit conserver au moins une variante.");
      return;
    }
    item.variants.splice(index, 1);
  }

  removeImage(item: ProductDraft, index: number): void {
    item.images.splice(index, 1);
    item.images.forEach((image, position) => (image.position = position));
  }

  async uploadImages(item: ProductDraft, event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files ?? []).slice(0, Math.max(0, 10 - item.images.length));
    if (!files.length) return;
    this.clearMessages();
    this.uploading.set(true);
    try {
      for (const file of files) {
        const result = await firstValueFrom(this.api.uploadImage(file));
        item.images.push({
          path: result.url,
          alt_text: item.name || "Article Staelle",
          position: item.images.length,
        });
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.uploading.set(false);
      input.value = "";
    }
  }

  saveProduct(item: ProductDraft): void {
    this.clearMessages();
    if (!item.name.trim() || !item.slug.trim() || !item.description.trim()) {
      this.error.set("Renseigne le nom, l’URL et la description de l’article.");
      return;
    }
    if (item.variants.some((variant) => !variant.sku.trim() || variant.selling_price <= 0)) {
      this.error.set("Chaque variante doit avoir un SKU et un prix valide.");
      return;
    }
    const payload = this.payload(item);
    const request = item.id
      ? this.api.updateProduct(item.id, payload)
      : this.api.createProduct(payload);
    this.busy.set(true);
    request.subscribe({
      next: () => {
        this.busy.set(false);
        this.closeEditor();
        this.feedback.set(item.id ? "Article mis à jour." : "Article ajouté au catalogue.");
        this.refreshData();
      },
      error: (error) => {
        this.busy.set(false);
        this.error.set(this.errorMessage(error));
      },
    });
  }

  archiveProduct(item: ProductDraft): void {
    if (!item.id) return;
    const confirmed = this.document.defaultView?.confirm(
      `Archiver « ${item.name} » ? Il ne sera plus visible dans la boutique.`,
    );
    if (!confirmed) return;
    this.api.archiveProduct(item.id).subscribe({
      next: () => {
        this.closeEditor();
        this.feedback.set("Article archivé.");
        this.refreshData();
      },
      error: (error) => this.error.set(this.errorMessage(error)),
    });
  }

  adjustStock(item: ProductDraft, variant: AdminProductVariant): void {
    if (!variant.id) return;
    this.clearMessages();
    this.busy.set(true);
    this.api
      .adjustStock({
        variant_id: variant.id,
        quantity_delta: Number(this.stockDelta()),
        kind: this.stockKind(),
        note: this.stockNote(),
      })
      .subscribe({
        next: () => {
          this.busy.set(false);
          this.feedback.set("Mouvement de stock enregistré.");
          this.closeEditor();
          this.refreshData();
        },
        error: (error) => {
          this.busy.set(false);
          this.error.set(this.errorMessage(error));
        },
      });
  }

  totalStock(product: AdminProduct): number {
    return product.variants.reduce(
      (total, variant) => total + (variant.available_stock ?? variant.stock_on_hand),
      0,
    );
  }

  minimumPrice(product: AdminProduct): number {
    return Math.min(...product.variants.map((variant) => variant.selling_price));
  }

  mainImage(product: AdminProduct): string {
    return product.images[0]?.path ?? "/images/product-adidas-bag.svg";
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat("fr-CM", {
      style: "currency",
      currency: "XAF",
      maximumFractionDigits: 0,
    }).format(price);
  }

  private emptyVariant(): AdminProductVariant {
    return {
      sku: "",
      size: null,
      color: null,
      selling_price: 0,
      compare_at_price: null,
      cost_price: null,
      stock_on_hand: 0,
      stock_reserved: 0,
      low_stock_threshold: 2,
      is_active: true,
    };
  }

  private payload(item: ProductDraft): AdminProductPayload {
    return {
      name: item.name.trim(),
      slug: item.slug.trim().toLowerCase(),
      brand: item.brand.trim(),
      category: item.category.trim(),
      description: item.description.trim(),
      status: item.status,
      featured: item.featured,
      variants: item.variants.map((variant) => ({
        id: variant.id,
        sku: variant.sku.trim().toUpperCase(),
        size: variant.size?.trim() || null,
        color: variant.color?.trim() || null,
        selling_price: Number(variant.selling_price),
        compare_at_price: variant.compare_at_price ? Number(variant.compare_at_price) : null,
        cost_price: variant.cost_price === null ? null : Number(variant.cost_price),
        stock_on_hand: Number(variant.stock_on_hand),
        stock_reserved: Number(variant.stock_reserved),
        low_stock_threshold: Number(variant.low_stock_threshold),
        is_active: variant.is_active,
      })),
      images: item.images.map((image, position) => ({
        path: image.path,
        alt_text: image.alt_text || item.name,
        position,
      })),
    };
  }

  private slugify(value: string): string {
    return this.normalize(value)
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }

  private normalize(value: string): string {
    return value
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  private clearMessages(): void {
    this.error.set("");
    this.feedback.set("");
  }

  private errorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const detail = error.error?.detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) return detail[0]?.msg ?? "Données invalides.";
    }
    return "Une erreur est survenue. Réessaie dans un instant.";
  }
}
