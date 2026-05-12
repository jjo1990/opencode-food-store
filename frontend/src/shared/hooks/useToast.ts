/**
 * useToast - Helper hook for showing toast notifications
 * Following FSD: shared/hooks/ directory
 */
import toast from 'react-hot-toast';

export function useToast() {
  const success = (message: string) => {
    toast.success(message);
  };

  const error = (message: string) => {
    toast.error(message);
  };

  const loading = (message: string) => {
    return toast.loading(message);
  };

  const dismiss = () => {
    toast.dismiss();
  };

  const dismissLoading = (toastId: string | undefined) => {
    if (toastId) {
      toast.dismiss(toastId);
    }
  };

  return {
    success,
    error,
    loading,
    dismiss,
    dismissLoading,
  };
}

export default useToast;