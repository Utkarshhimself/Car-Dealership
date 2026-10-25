export type Vehicle = {
  id: string;
  make: string;
  model: string;
  category: string;
  price: string;
  quantity: number;
  image_filename: string | null;
  created_at: string;
  updated_at: string;
};

export type VehiclePage = {
  items: Vehicle[];
  page: number;
  page_size: number;
  total: number;
};

export type VehicleInput = {
  make: string;
  model: string;
  category: string;
  price: number;
  quantity: number;
};
