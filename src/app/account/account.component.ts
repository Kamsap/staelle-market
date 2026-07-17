import { HttpErrorResponse } from "@angular/common/http";
import { Component, inject, signal } from "@angular/core";
import { FormsModule, NgForm } from "@angular/forms";
import { AuthService } from "../auth.service";

type AccountMode = "choice" | "login" | "register";

@Component({
  selector: "app-account",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./account.component.html",
  styleUrl: "./account.component.scss",
})
export class AccountComponent {
  readonly auth = inject(AuthService);
  readonly mode = signal<AccountMode>("choice");
  readonly loading = signal(false);
  readonly errorMessage = signal("");
  readonly guestMessage = signal("");

  loginData = { email: "", password: "" };
  registerData = { full_name: "", email: "", phone: "", password: "" };

  chooseGuest(): void {
    this.mode.set("choice");
    this.guestMessage.set(
      "Tu peux commander sans compte. Aucun point ne sera cumulé.",
    );
  }

  login(form: NgForm): void {
    if (form.invalid) return form.control.markAllAsTouched();
    this.submit(() => this.auth.login(this.loginData));
  }

  register(form: NgForm): void {
    if (form.invalid) return form.control.markAllAsTouched();
    this.submit(() => this.auth.register(this.registerData));
  }

  logout(): void {
    this.auth.logout();
    this.mode.set("choice");
  }

  show(mode: AccountMode): void {
    this.errorMessage.set("");
    this.guestMessage.set("");
    this.mode.set(mode);
  }

  private submit(request: () => ReturnType<AuthService["login"]>): void {
    this.loading.set(true);
    this.errorMessage.set("");
    request().subscribe({
      next: () => this.loading.set(false),
      error: (error: HttpErrorResponse) => {
        this.loading.set(false);
        this.errorMessage.set(
          error.error?.detail ??
            "Le service est indisponible. Réessaie plus tard.",
        );
      },
    });
  }
}
