import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="px-4 lg:px-6 h-14 flex items-center border-b">
        <Link className="flex items-center justify-center" href="#">
          <span className="font-bold text-xl">🧪 TestFlow</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline" href="/login">
            Login
          </Link>
          <Link className="text-sm font-medium hover:underline" href="/register">
            Register
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Modern Test Management
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl">
                  Streamline your QA process with TestFlow. Powerful test case management, 
                  CI/CD integration, and real-time analytics.
                </p>
              </div>
              <div className="space-x-4">
                <Link href="/register" className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700">
                  Get Started
                </Link>
                <Link href="/login" className="border border-gray-300 px-8 py-3 rounded-md hover:bg-gray-50">
                  Login
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}