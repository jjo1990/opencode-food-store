/**
 * Toast Container - Container for react-hot-toast notifications
 * Following FSD: shared/components/ directory
 */
import { Toaster } from 'react-hot-toast';

export function ToastContainer() {
  return (
    <Toaster
      position="top-right"
      reverseOrder={false}
      toastOptions={{
        duration: 4000,
        style: { background: '#363636', color: '#fff' },
        success: { duration: 3000 },
        error: { duration: 5000 },
      }}
    />
  );
}

export default ToastContainer;