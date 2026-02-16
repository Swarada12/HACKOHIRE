import './globals.css';
import Sidebar from './components/Sidebar';

export const metadata = {
  title: 'Barclays EWS — Early Warning System',
  description: 'Proactive delinquency prediction platform powered by ML — detect financial stress signals early and enable empathetic interventions before missed payments.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="app-layout">
          <Sidebar />
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
