import { Component, inject } from "@angular/core";
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { PICKUP_POINTS, PickupPoint } from "./pickup-points";

interface PickupPointView extends PickupPoint {
  directionsUrl: string;
  mapEmbedUrl: SafeResourceUrl;
}

@Component({
  selector: "app-pickup-points",
  standalone: true,
  templateUrl: "./pickup-points.component.html",
  styleUrl: "./pickup-points.component.scss",
})
export class PickupPointsComponent {
  private readonly sanitizer = inject(DomSanitizer);

  /**
   * On transforme les données simples en liens Google Maps prêts à afficher.
   * Pour ajouter ou modifier un lieu, il suffit d'éditer pickup-points.ts.
   */
  readonly points: PickupPointView[] = PICKUP_POINTS.map((point) => {
    const query = encodeURIComponent(point.mapQuery);
    return {
      ...point,
      directionsUrl: `https://www.google.com/maps/dir/?api=1&destination=${query}`,
      mapEmbedUrl: this.sanitizer.bypassSecurityTrustResourceUrl(
        `https://www.google.com/maps?q=${query}&z=16&output=embed`,
      ),
    };
  });
}
