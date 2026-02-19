import './globals.css';
import Sidebar from './components/Sidebar';
import { RealtimeProvider } from './context/RealtimeContext';

export const metadata = {
  title: 'Praeventix EWS — Early Warning System',
  description: 'Proactive delinquency prediction platform powered by ML — detect financial stress signals early and enable empathetic interventions before missed payments.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <RealtimeProvider>
          <div className="app-layout">
            <Sidebar />
            <main className="main-content">
              {children}
            </main>
          </div>
        </RealtimeProvider>
      </body>
    </html>
  );
}
