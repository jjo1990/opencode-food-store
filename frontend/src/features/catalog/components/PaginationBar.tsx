import { Pagination } from '../../../shared/components/Pagination';

interface PaginationBarProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function PaginationBar({ currentPage, totalPages, onPageChange }: PaginationBarProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="mt-8 flex items-center justify-between">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Página {currentPage} de {totalPages}
      </p>
      <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} />
    </div>
  );
}

export default PaginationBar;
