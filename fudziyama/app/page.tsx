import { categories, getProductsByCategory } from "@/lib/products";
import { Hero } from "@/components/hero";
import { CategoryNav } from "@/components/category-nav";
import { ProductCard } from "@/components/product-card";

export default function HomePage() {
  return (
    <>
      <Hero />
      <CategoryNav categories={categories} />

      <div className="container flex flex-col gap-14 py-10">
        {categories.map((category) => {
          const categoryProducts = getProductsByCategory(category.id);
          if (categoryProducts.length === 0) return null;

          return (
            <section
              key={category.id}
              id={`category-${category.id}`}
              className="scroll-mt-32"
              aria-labelledby={`heading-${category.id}`}
            >
              <h2
                id={`heading-${category.id}`}
                className="mb-6 text-2xl font-bold tracking-tight sm:text-3xl"
              >
                {category.title}
              </h2>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {categoryProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </>
  );
}
