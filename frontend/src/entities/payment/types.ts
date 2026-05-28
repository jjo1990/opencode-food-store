export interface PaymentResult {
  mp_payment_id: string | null;
  status: string;
  status_detail: string | null;
}

export interface PaymentHistoryItem {
  mp_payment_id: string | null;
  mp_status: string;
  status_detail: string | null;
  created_at: string;
}

export interface PaymentHistory {
  pagos: PaymentHistoryItem[];
}

export type CheckoutStep = 'review' | 'processing' | 'success' | 'failure' | 'pending';
