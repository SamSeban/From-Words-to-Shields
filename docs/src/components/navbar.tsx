import { Download } from 'lucide-react';

const Navbar: React.FC = () => {
  
  return (
    <nav className="bg-gray-900 text-white py-8 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        
        {/* Title and Subtitle (Big, centered, bold) */}
        <div className="text-center mb-5">
          <h1 className="text-4xl font-extrabold md:text-5xl tracking-tight">
            From Words to Shields: Agentic Privacy for Smart Sensors
          </h1>
          <p className="text-gray-400 mt-2 text-lg font-medium">
            Course project website for EC M202A / CS M213A at UCLA
          </p>
        </div>
        {/* Download Links (minimal, with icons) */}
        <div className="flex items-center text-sm font-medium" style={{ gap: '3rem' }}>
          {/* GitHub Repo Link (Kept original SVG for GitHub logo consistency) */}
          <a 
            href="https://github.com/SamSeban/From-Words-to-Shields" 
            className="flex items-center text-indigo-400 hover:text-indigo-300 transition-colors" 
            style={{ gap: '0.5rem' }}
            target="_blank"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.803 8.232 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.542-1.36-.295-1.921-.295-1.921-1.115-.76-.088-1.171.083-1.171.97.067 1.4.995 1.4.995.862 1.493 2.228 1.06 2.76.804.084-.626.337-1.06.612-1.303-2.665-.3-5.466-1.333-5.466-5.93 0-1.31.465-2.382 1.235-3.221-.124-.301-.535-1.523.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.046.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.875.118 3.176.77.839 1.233 1.911 1.233 3.221 0 4.609-2.805 5.624-5.475 5.921.346.297.662.887.662 1.792 0 1.303-.01 2.355-.01 2.684 0 .323.218.693.823.578 4.792-1.583 8.225-6.084 8.225-11.385 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span>GitHub Repo</span>
          </a>
          
          {/* ZIP Download Link (Now with Download icon) */}
          <a 
            href="#zip-download" 
            className="flex items-center text-indigo-400 hover:text-indigo-300 transition-colors" 
            style={{ gap: '0.5rem' }}
            onClick={(e) => { e.preventDefault(); console.log('Simulating link click to Download ZIP'); }}
          >
            <Download className="w-5 h-5" />
            <span>Download ZIP</span>
          </a>
          
          {/* TAR Download Link (Now with Download icon) */}
          <a 
            href="#tar-download" 
            className="flex items-center text-indigo-400 hover:text-indigo-300 transition-colors" 
            style={{ gap: '0.5rem' }}
            onClick={(e) => { e.preventDefault(); console.log('Simulating link click to Download TAR'); }}
          >
            <Download className="w-5 h-5" />
            <span>Download TAR</span>
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;