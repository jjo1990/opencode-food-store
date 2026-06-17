import { useState } from 'react';
import { Skeleton } from '../../../shared/components/Skeleton';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import type { Category } from '../../../entities/category/types';

interface CategoryNavProps {
  categories: Category[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  selectedCategoryId: string | null;
  onSelectCategory: (id: string | null) => void;
  onRetry: () => void;
}

function CategoryNode({
  category,
  selectedCategoryId,
  onSelectCategory,
  depth,
}: {
  category: Category;
  selectedCategoryId: string | null;
  onSelectCategory: (id: string | null) => void;
  depth: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = category.children && category.children.length > 0;
  const isSelected = selectedCategoryId === category.id;

  return (
    <li>
      <div
        className={`flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
          isSelected ? 'bg-primary-50 font-medium text-primary' : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
        }`}
        style={{ paddingLeft: `${12 + depth * 16}px` }}
        onClick={() => {
          if (hasChildren) {
            setExpanded(!expanded);
          } else {
            onSelectCategory(isSelected ? null : category.id);
          }
        }}
      >
        {hasChildren && (
          <svg
            className={`h-3.5 w-3.5 transition-transform ${expanded ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        )}
        <span>{category.nombre}</span>
      </div>
      {hasChildren && expanded && (
        <ul>
          {category.children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={onSelectCategory}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function CategoryNav({
  categories,
  isLoading,
  isError,
  error,
  selectedCategoryId,
  onSelectCategory,
  onRetry,
}: CategoryNavProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="45%" />
        <Skeleton variant="text" width="70%" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorDisplay message={error?.message || 'Error al cargar categorías'} onRetry={onRetry} />
    );
  }

  return (
    <nav>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
        Categorías
      </h3>
      <ul className="space-y-0.5">
        <li>
          <button
            className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
              selectedCategoryId === null
                ? 'bg-primary-50 font-medium text-primary'
                : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
            onClick={() => onSelectCategory(null)}
          >
            Todas las categorías
          </button>
        </li>
        {categories?.map((cat) => (
          <CategoryNode
            key={cat.id}
            category={cat}
            selectedCategoryId={selectedCategoryId}
            onSelectCategory={onSelectCategory}
            depth={0}
          />
        ))}
      </ul>
    </nav>
  );
}

export default CategoryNav;
