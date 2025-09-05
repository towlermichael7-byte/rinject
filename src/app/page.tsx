'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileUpload } from '@/components/FileUpload'
import { ResumeProcessor } from '@/components/ResumeProcessor'
import { RequirementsManager } from '@/components/RequirementsManager'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface UploadedFile {
  file: File
  id: string
}

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Resume Customizer Pro
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Customize your resume and send it to multiple recipients with advanced 
          multi-user features, smart email automation, and high-performance processing.
        </p>
      </div>

      <Tabs defaultValue="customizer" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="customizer">📄 Resume Customizer</TabsTrigger>
          <TabsTrigger value="bulk">📤 Bulk Processor</TabsTrigger>
          <TabsTrigger value="requirements">📋 Requirements</TabsTrigger>
          <TabsTrigger value="settings">⚙️ Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="customizer" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload Resume Files</CardTitle>
            </CardHeader>
            <CardContent>
              <FileUpload onFilesChange={setUploadedFiles} />
            </CardContent>
          </Card>

          <ResumeProcessor files={uploadedFiles} />
        </TabsContent>

        <TabsContent value="bulk" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Bulk Processing</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <h3 className="text-lg font-semibold mb-2">High-Performance Bulk Processing</h3>
                <p className="text-gray-600 mb-4">
                  Process multiple resumes simultaneously for maximum speed and efficiency.
                </p>
                <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">50+</div>
                    <div className="text-sm text-gray-500">Concurrent Users</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">8x</div>
                    <div className="text-sm text-gray-500">Faster Processing</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">∞</div>
                    <div className="text-sm text-gray-500">Scalability</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements" className="space-y-6">
          <RequirementsManager />
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Application Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Performance Configuration</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Max Workers</label>
                      <input 
                        type="number" 
                        className="w-full p-2 border rounded-md" 
                        defaultValue={4}
                        min={1}
                        max={8}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Bulk Mode Threshold</label>
                      <input 
                        type="number" 
                        className="w-full p-2 border rounded-md" 
                        defaultValue={3}
                        min={2}
                        max={10}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Email Configuration</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">SMTP Server</label>
                      <select className="w-full p-2 border rounded-md">
                        <option>smtp.gmail.com</option>
                        <option>smtp.office365.com</option>
                        <option>smtp.mail.yahoo.com</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">SMTP Port</label>
                      <input 
                        type="number" 
                        className="w-full p-2 border rounded-md" 
                        defaultValue={587}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      Enable rate limiting
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      Validate file types
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      Enable audit logging
                    </label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <footer className="text-center py-8 border-t">
        <p className="text-gray-600">
          <strong>Resume Customizer Pro v2.1.0</strong> | 
          Enhanced with Security & Performance Monitoring | 
          Built with Next.js, TypeScript, and Supabase
        </p>
      </footer>
    </div>
  )
}