export type Theme = "paper" | "sepia" | "night";

export type CatNode = {
  id: string;
  title: string;
  pali?: string;
  route: string;
  path?: string;
  source?: string;
  leafCount?: number;
  children?: CatNode[];
};

export type Collection = {
  id: string;
  title: string;
  blurb: string;
  volumes: CatNode[];
};

export type Catalog = {
  title: string;
  subtitle: string;
  collections: Collection[];
};

export type Settings = {
  theme: Theme;
  fontSize: number;
};
