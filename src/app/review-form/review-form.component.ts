import { DOCUMENT } from "@angular/common";
import { Component, inject, signal } from "@angular/core";
import { FormsModule, NgForm } from "@angular/forms";
import { STORE_CONFIG } from "../store.config";

/** Données saisies par le client dans le formulaire d'avis. */
interface ReviewFormData {
  name: string;
  phone: string;
  email: string;
  message: string;
}

@Component({
  selector: "app-review-form",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./review-form.component.html",
  styleUrl: "./review-form.component.scss",
})
export class ReviewFormComponent {
  private readonly document = inject(DOCUMENT);

  /** Objet lié aux champs grâce à [(ngModel)]. */
  review: ReviewFormData = this.emptyReview();

  /** Message lu par les technologies d'assistance après l'envoi. */
  readonly feedbackMessage = signal("");

  /** Longueur affichée sous la zone de texte. */
  get messageLength(): number {
    return this.review.message.length;
  }

  sendReview(form: NgForm): void {
    // Si un champ est incorrect, on affiche ses erreurs et on n'ouvre pas WhatsApp.
    if (form.invalid) {
      form.control.markAllAsTouched();
      this.feedbackMessage.set(
        "Vérifie les champs indiqués avant de continuer.",
      );
      return;
    }

    const text = [
      "Bonjour Staelle Market, je souhaite laisser un avis.",
      "",
      `Nom : ${this.review.name}`,
      `Téléphone : ${this.review.phone}`,
      `E-mail : ${this.review.email}`,
      "",
      `Avis : ${this.review.message}`,
    ].join("\n");

    const url = `https://wa.me/${STORE_CONFIG.whatsappNumber}?text=${encodeURIComponent(text)}`;

    // defaultView représente la fenêtre du navigateur sans utiliser directement window.
    const whatsappWindow = this.document.defaultView?.open(url, "_blank");

    if (whatsappWindow) {
      // Empêche le nouvel onglet d'accéder à la page de la boutique.
      whatsappWindow.opener = null;
      this.feedbackMessage.set(
        "WhatsApp s’est ouvert avec ton avis prêt à être envoyé.",
      );
    } else {
      this.feedbackMessage.set(
        "Le navigateur a bloqué WhatsApp. Autorise les fenêtres contextuelles puis réessaie.",
      );
    }
  }

  private emptyReview(): ReviewFormData {
    return { name: "", phone: "", email: "", message: "" };
  }
}
