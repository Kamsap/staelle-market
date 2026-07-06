import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Product, PRODUCTS } from './products';
type FilterValue = 'Tous' | Product['brand'] | Product['category'];
@Component({selector:'app-root',standalone:true,imports:[FormsModule],templateUrl:'./app.component.html',styleUrl:'./app.component.scss'})
export class AppComponent {
  readonly whatsappNumber='237690000000';
  readonly products=signal(PRODUCTS); readonly search=signal(''); readonly brand=signal<FilterValue>('Tous'); readonly category=signal<FilterValue>('Tous'); readonly availability=signal<'Tous'|'Disponible'>('Tous');
  readonly brands=['Tous','Nike','Adidas','Autre'] as const; readonly categories=['Tous','Sac','Chaussure','Vêtement','Accessoire'] as const;
  readonly filteredProducts=computed(()=>{const search=this.normalize(this.search()),brand=this.brand(),category=this.category(),availability=this.availability();return this.products().filter(product=>(!search||this.normalize(`${product.name} ${product.brand} ${product.category} ${product.description}`).includes(search))&&(brand==='Tous'||product.brand===brand)&&(category==='Tous'||product.category===category)&&(availability==='Tous'||product.stock>0));});
  status(product:Product):'Disponible'|'Stock limité'|'Rupture'{if(product.stock<=0)return'Rupture';if(product.stock<=2)return'Stock limité';return'Disponible'}
  whatsappLink(product?:Product):string{const base=`https://wa.me/${this.whatsappNumber}`;const text=product?`Bonjour Staelle Market, je suis intéressé par cet article : ${product.name} (${product.brand}) à ${this.formatPrice(product.price)}.`:'Bonjour Staelle Market, je souhaite avoir plus d’informations sur vos articles.';return`${base}?text=${encodeURIComponent(text)}`}
  formatPrice(price:number):string{return new Intl.NumberFormat('fr-CM',{style:'currency',currency:'XAF',maximumFractionDigits:0}).format(price)}
  private normalize(value:string):string{return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim()}
}
