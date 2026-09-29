import type {
  Booking,
  Building,
  Company,
  Department,
  Desk,
  DeskWithOccupant,
  User,
  Zone,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', status: number = 500) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('myaloca_token');
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errCode = 'HTTP_ERROR';
    let errMsg = `Request failed with status ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        if (typeof errData.detail === 'object') {
          errCode = errData.detail.code || errCode;
          errMsg = errData.detail.message || errMsg;
        } else {
          errMsg = errData.detail;
        }
      }
    } catch {
      // not JSON
    }
    throw new ApiError(errMsg, errCode, response.status);
  }

  return response.json();
}

export const api = {
  auth: {
    async login(email: string, password: string): Promise<{ access_token: string }> {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const msg = err.detail?.message || 'Falha ao autenticar usuário';
        const code = err.detail?.code || 'AUTH_ERROR';
        throw new ApiError(msg, code, response.status);
      }

      return response.json();
    },

    async getMe(): Promise<User> {
      return request<User>('/auth/me');
    },

    async updateMe(data: Partial<User> & { password?: string }): Promise<User> {
      return request<User>('/auth/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    async register(data: Partial<User> & { password: string }): Promise<User> {
      return request<User>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  users: {
    async list(params?: {
      role?: string;
      department?: string;
      search?: string;
      is_active?: boolean;
    }): Promise<User[]> {
      const q = new URLSearchParams();
      if (params?.role) q.append('role', params.role);
      if (params?.department) q.append('department', params.department);
      if (params?.search) q.append('search', params.search);
      if (params?.is_active !== undefined) q.append('is_active', params.is_active.toString());
      const queryStr = q.toString() ? `?${q.toString()}` : '';
      return request<User[]>(`/users${queryStr}`);
    },

    async get(id: number): Promise<User> {
      return request<User>(`/users/${id}`);
    },

    async create(data: Partial<User> & { password: string }): Promise<User> {
      return request<User>('/users', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    async update(id: number, data: Partial<User> & { password?: string }): Promise<User> {
      return request<User>(`/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/users/${id}`, {
        method: 'DELETE',
      });
    },
  },

  departments: {
    async list(params?: {
      company_id?: number;
      is_active?: boolean;
      search?: string;
    }): Promise<Department[]> {
      const q = new URLSearchParams();
      if (params?.company_id !== undefined) q.append('company_id', params.company_id.toString());
      if (params?.is_active !== undefined) q.append('is_active', params.is_active.toString());
      if (params?.search) q.append('search', params.search);
      const queryStr = q.toString() ? `?${q.toString()}` : '';
      return request<Department[]>(`/departments${queryStr}`);
    },

    async get(id: number): Promise<Department> {
      return request<Department>(`/departments/${id}`);
    },

    async create(data: Partial<Department>): Promise<Department> {
      return request<Department>('/departments', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    async update(id: number, data: Partial<Department>): Promise<Department> {
      return request<Department>(`/departments/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/departments/${id}`, {
        method: 'DELETE',
      });
    },
  },

  companies: {
    async list(): Promise<Company[]> {
      return request<Company[]>('/companies');
    },
    async get(id: number): Promise<Company> {
      return request<Company>(`/companies/${id}`);
    },
    async create(data: {
      name: string;
      code: string;
      cnpj?: string | null;
      description?: string | null;
      is_active?: boolean;
    }): Promise<Company> {
      return request<Company>('/companies', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: number, data: Partial<Company>): Promise<Company> {
      return request<Company>(`/companies/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/companies/${id}`, {
        method: 'DELETE',
      });
    },
  },

  buildings: {
    async list(companyId?: number): Promise<Building[]> {
      const q = companyId !== undefined ? `?company_id=${companyId}` : '';
      return request<Building[]>(`/buildings${q}`);
    },
    async get(id: number): Promise<Building> {
      return request<Building>(`/buildings/${id}`);
    },
    async create(data: {
      name: string;
      code: string;
      company_id?: number | null;
      address?: string | null;
      city?: string | null;
      total_floors?: number;
      is_active?: boolean;
    }): Promise<Building> {
      return request<Building>('/buildings', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: number, data: Partial<Building>): Promise<Building> {
      return request<Building>(`/buildings/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/buildings/${id}`, {
        method: 'DELETE',
      });
    },
  },

  zones: {
    async list(floor?: number, buildingId?: number): Promise<Zone[]> {
      const params = new URLSearchParams();
      if (floor !== undefined) params.append('floor', floor.toString());
      if (buildingId !== undefined) params.append('building_id', buildingId.toString());
      const q = params.toString() ? `?${params.toString()}` : '';
      return request<Zone[]>(`/zones${q}`);
    },
    async get(id: number): Promise<Zone> {
      return request<Zone>(`/zones/${id}`);
    },
    async create(data: Partial<Zone> & { name: string }): Promise<Zone> {
      return request<Zone>('/zones', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: number, data: Partial<Zone>): Promise<Zone> {
      return request<Zone>(`/zones/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/zones/${id}`, {
        method: 'DELETE',
      });
    },
  },

  desks: {
    async list(zoneId?: number, floor?: number): Promise<Desk[]> {
      const params = new URLSearchParams();
      if (zoneId !== undefined) params.append('zone_id', zoneId.toString());
      if (floor !== undefined) params.append('floor', floor.toString());
      const q = params.toString() ? `?${params.toString()}` : '';
      return request<Desk[]>(`/desks${q}`);
    },
    async get(id: number): Promise<Desk> {
      return request<Desk>(`/desks/${id}`);
    },
    async create(data: Partial<Desk>): Promise<Desk> {
      return request<Desk>('/desks', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async createBatch(desks: Partial<Desk>[]): Promise<Desk[]> {
      return request<Desk[]>('/desks/batch', {
        method: 'POST',
        body: JSON.stringify(desks),
      });
    },
    async update(id: number, data: Partial<Desk>): Promise<Desk> {
      return request<Desk>(`/desks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    getQrCodeUrl(id: number): string {
      return `${API_BASE_URL}/desks/${id}/qrcode`;
    },
    async downloadQrCode(id: number, deskCode: string): Promise<void> {
      const url = `${API_BASE_URL}/desks/${id}/qrcode`;
      const token = localStorage.getItem('myaloca_token');
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(url, { headers });
      if (!response.ok) {
        throw new Error('Falha ao baixar imagem do QR Code');
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = objectUrl;
      a.download = `myaloca-baia-${deskCode.toLowerCase()}-qr.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(objectUrl);
    },
    async delete(id: number): Promise<{ code: string; message: string }> {
      return request<{ code: string; message: string }>(`/desks/${id}`, {
        method: 'DELETE',
      });
    },
    async release(id: number): Promise<Desk> {
      return request<Desk>(`/desks/${id}/release`, {
        method: 'POST',
      });
    },
  },

  bookings: {
    async create(data: {
      desk_id: number;
      start_time: string;
      end_time: string;
      notes?: string;
    }): Promise<Booking> {
      return request<Booking>('/bookings', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async cancel(bookingId: number): Promise<Booking> {
      return request<Booking>(`/bookings/${bookingId}/cancel`, {
        method: 'POST',
      });
    },
    async checkout(bookingId: number): Promise<Booking> {
      return request<Booking>(`/bookings/${bookingId}/checkout`, {
        method: 'POST',
      });
    },
    async checkIn(bookingId: number, qrCodeHash: string): Promise<Booking> {
      return request<Booking>(`/bookings/${bookingId}/checkin`, {
        method: 'POST',
        body: JSON.stringify({ qr_code_hash: qrCodeHash }),
      });
    },
    async listMy(): Promise<Booking[]> {
      return request<Booking[]>('/bookings/me');
    },
    async get3dOffice(zoneId?: number, floor?: number): Promise<DeskWithOccupant[]> {
      const params = new URLSearchParams();
      if (zoneId !== undefined) params.append('zone_id', zoneId.toString());
      if (floor !== undefined) params.append('floor', floor.toString());
      const q = params.toString() ? `?${params.toString()}` : '';
      return request<DeskWithOccupant[]>(`/bookings/3d-office${q}`);
    },
  },
};
