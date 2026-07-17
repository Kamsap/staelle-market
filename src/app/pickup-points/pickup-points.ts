export interface PickupPoint {
  id: string;
  name: string;
  area: string;
  address: string;
  mapQuery: string;
  note: string;
}

export const PICKUP_POINTS: PickupPoint[] = [
  {
    id: "reference-pressing-lonkak",
    name: "Accueil de Référence Pressing",
    area: "Lonkak · Yaoundé",
    address: "Vallée Nlongkak, rue du Famous, Yaoundé",
    mapQuery: "Référence Pressing, Vallée Nlongkak, Yaoundé, Cameroun",
    note: "Retrait après confirmation de la commande sur WhatsApp.",
  },
  {
    id: "ecole-nkolmesseng",
    name: "École publique de Nkolmesseng",
    area: "Nkolmesseng · Yaoundé V",
    address: "École publique de Nkolmesseng, Yaoundé",
    mapQuery: "3.88668,11.56815",
    note: "Rendez-vous devant l’école après confirmation sur WhatsApp.",
  },
  {
    id: "entree-beac-yaounde",
    name: "Entrée principale de la BEAC",
    area: "Centre-ville · Yaoundé",
    address: "736 avenue Monseigneur Vogt, Yaoundé",
    mapQuery: "BEAC Siège, 736 avenue Monseigneur Vogt, Yaoundé, Cameroun",
    note: "Rendez-vous à l’entrée principale après confirmation sur WhatsApp.",
  },
];
