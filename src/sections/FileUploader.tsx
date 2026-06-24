import { useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';

interface FileUploaderProps {
  onFileUpload: (file: File) => void;
  fileName: string;
  loading: boolean;
  error: string | null;
}

export function FileUploader({ onFileUpload, fileName, loading, error }: FileUploaderProps) {
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
        onFileUpload(file);
      }
    }
  }, [onFileUpload]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  }, [onFileUpload]);

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Auto-Alimentación de Datos (NOC-Sync)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            loading 
              ? 'border-blue-300 bg-blue-50' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          {loading ? (
            <div className="flex flex-col items-center gap-2">
              <RefreshCw className="h-8 w-8 text-blue-500 animate-spin" />
              <p className="text-sm text-blue-600 font-medium">Procesando archivo...</p>
            </div>
          ) : (
            <>
              <FileSpreadsheet className="h-10 w-10 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-muted-foreground mb-2">
                Arrastre archivos Excel aquí o haga clic para seleccionar
              </p>
              <p className="text-xs text-muted-foreground mb-3">
                Soporta: Statistics (Eb/No), Statistics (Traffic), VNO Data Usage Report
              </p>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileInput}
                className="hidden"
                id="file-upload"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                <Upload className="h-4 w-4 mr-1" />
                Seleccionar Archivo
              </Button>
            </>
          )}
        </div>

        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {fileName && !loading && (
          <div className="mt-3 p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <div>
              <p className="text-sm text-emerald-700 font-medium">Archivo procesado exitosamente</p>
              <p className="text-xs text-emerald-600">{fileName}</p>
            </div>
          </div>
        )}

        <div className="mt-4 space-y-2">
          <p className="text-xs font-medium text-muted-foreground">Formatos soportados:</p>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="text-xs">
              <FileSpreadsheet className="h-3 w-3 mr-1" />
              statistics(26).xlsx - Eb/No
            </Badge>
            <Badge variant="outline" className="text-xs">
              <FileSpreadsheet className="h-3 w-3 mr-1" />
              statistics(27).xlsx - Traffic
            </Badge>
            <Badge variant="outline" className="text-xs">
              <FileSpreadsheet className="h-3 w-3 mr-1" />
              VNO Data Usage Report.xlsx
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
