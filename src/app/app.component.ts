import { DOCUMENT } from "@angular/common";
import {
  Component,
  computed,
  HostListener,
  inject,
  signal,
} from "@angular/core";
import { FormsModule } from "@angular/forms";
import { toSignal } from "@angular/core/rxjs-interop";
import { AccountComponent } from "./account/account.component";
import { CatalogService } from "./catalog.service";
import { OrderService } from "./order.service";
import { PickupPointsComponent } from "./pickup-points/pickup-points.component";
import { Product, PRODUCTS } from "./products";
import { ReviewFormComponent } from "./review-form/review-form.component";
import { STORE_CONFIG } from "./store.config";

type FilterValue = "Tous" | Product["brand"] | Product["category"];

@Component({
  selector: "app-root",
  standalone: true,
  imports: [
    FormsModule,
    AccountComponent,
    PickupPointsComponent,
    ReviewFormComponent,
  ],
  templateUrl: "./app.component.html",
  styleUrl: "./app.component.scss",
})
export class AppComponent {
  // Services injectés : accès au navigateur et chargement du catalogue.
  private readonly document = inject(DOCUMENT);
  private readonly catalogService = inject(CatalogService);
  private readonly orderService = inject(OrderService);

  // Configuration et données principales de la boutique.
  readonly whatsappNumber = STORE_CONFIG.whatsappNumber;
  readonly products = toSignal(this.catalogService.getProducts(), {
    initialValue: PRODUCTS,
  });
  readonly heroPrice = PRODUCTS.find((item) => item.id === 58)?.price ?? 0;

  // État des filtres. Un signal contient une valeur qui peut changer dans l'interface.
  readonly search = signal("");
  readonly brand = signal<FilterValue>("Tous");
  readonly category = signal<FilterValue>("Tous");
  readonly availability = signal<"Tous" | "Disponible">("Tous");
  readonly visibleCount = signal(12);
  readonly selectedViews = signal<Record<number, number>>({});

  // État de la galerie plein écran.
  readonly galleryProduct = signal<Product | null>(null);
  readonly galleryIndex = signal(0);
  readonly galleryImage = computed(() => {
    const product = this.galleryProduct();
    return product?.images[this.galleryIndex()] ?? product?.image ?? "";
  });
  readonly brands = ["Tous", "Nike", "Adidas", "Autre"] as const;
  readonly categories = [
    "Tous",
    "Sac",
    "Chaussure",
    "Vêtement",
    "Accessoire",
  ] as const;

  // Liste recalculée automatiquement dès qu'un filtre change.
  readonly filteredProducts = computed(() => {
    const search = this.normalize(this.search());
    return this.products().filter(
      (item) =>
        (!search ||
          this.normalize(
            `${item.name} ${item.brand} ${item.category} ${item.color ?? ""}`,
          ).includes(search)) &&
        (this.brand() === "Tous" || item.brand === this.brand()) &&
        (this.category() === "Tous" || item.category === this.category()) &&
        (this.availability() === "Tous" || item.stock > 0),
    );
  });
  readonly displayedProducts = computed(() =>
    this.filteredProducts().slice(0, this.visibleCount()),
  );
  readonly remainingProducts = computed(() =>
    Math.max(0, this.filteredProducts().length - this.visibleCount()),
  );

  // --- Actions du catalogue -------------------------------------------------

  showMore(): void {
    this.visibleCount.update((count) => count + 12);
  }
  activeImage(item: Product): string {
    return item.images[this.selectedViews()[item.id] ?? 0] ?? item.image;
  }
  selectView(productId: number, index: number): void {
    this.selectedViews.update((views) => ({ ...views, [productId]: index }));
  }

  // --- Actions de la galerie ------------------------------------------------

  openGallery(item: Product): void {
    this.galleryProduct.set(item);
    this.galleryIndex.set(this.selectedViews()[item.id] ?? 0);
    this.document.body.style.overflow = "hidden";
  }
  closeGallery(): void {
    this.galleryProduct.set(null);
    this.document.body.style.overflow = "";
  }
  selectGalleryView(index: number): void {
    const product = this.galleryProduct();
    if (!product?.images[index]) return;
    this.galleryIndex.set(index);
    this.selectView(product.id, index);
  }
  previousGalleryView(): void {
    const count = this.galleryProduct()?.images.length ?? 0;
    if (count > 1)
      this.selectGalleryView((this.galleryIndex() - 1 + count) % count);
  }
  nextGalleryView(): void {
    const count = this.galleryProduct()?.images.length ?? 0;
    if (count > 1) this.selectGalleryView((this.galleryIndex() + 1) % count);
  }
  @HostListener("document:keydown", ["$event"])
  handleGalleryKeyboard(event: KeyboardEvent): void {
    if (!this.galleryProduct()) return;
    if (event.key === "Escape") this.closeGallery();
    if (event.key === "ArrowLeft") this.previousGalleryView();
    if (event.key === "ArrowRight") this.nextGalleryView();
  }

  // --- Affichage et liens ---------------------------------------------------

  status(item: Product): "Disponible" | "Stock limité" | "Rupture" {
    if (item.stock <= 0) return "Rupture";
    if (item.stock <= 2) return "Stock limité";
    return "Disponible";
  }
  orderProduct(item: Product): void {
    if (item.stock <= 0) return;

    const reference = `SM-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;

    // L'enregistrement n'empêche jamais un invité de poursuivre sa commande.
    this.orderService
      .trackOrder(item, reference)
      .subscribe({ error: () => undefined });
    this.document.defaultView?.open(
      this.whatsappLink(item, reference),
      "_blank",
    );
  }

  whatsappLink(item?: Product, reference?: string): string {
    const base = `https://wa.me/${this.whatsappNumber}`;
    const text = item
      ? `Bonjour Staelle Market, je suis intéressé par cet article : ${item.name} (${item.brand}) à ${this.formatPrice(item.price)}.${reference ? ` Référence : ${reference}.` : ""}`
      : "Bonjour Staelle Market, je souhaite avoir plus d’informations sur vos articles.";
    return `${base}?text=${encodeURIComponent(text)}`;
  }
  formatPrice(price: number): string {
    return new Intl.NumberFormat(STORE_CONFIG.locale, {
      style: "currency",
      currency: STORE_CONFIG.currency,
      maximumFractionDigits: 0,
    }).format(price);
  }
  private normalize(value: string): string {
    // Retirer les accents permet à "vetement" de trouver aussi "Vêtement".
    return value
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }
}
