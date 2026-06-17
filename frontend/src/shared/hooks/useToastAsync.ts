import toast from 'react-hot-toast';

export function useToastAsync() {
  const promise = <T>(
    promiseFn: Promise<T>,
    messages: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: unknown) => string);
    },
  ) => toast.promise<T>(promiseFn, messages);

  return { promise };
}

export default useToastAsync;
