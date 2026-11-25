package app.lookupsafe

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.net.Uri
import androidx.core.content.FileProvider
import java.io.File

object ImageSharing {
    private fun directory(context:Context): File = File(context.cacheDir,"images").apply { mkdirs() }
    fun newPhoto(context:Context): Uri {
        val dir=directory(context)
        dir.listFiles()?.filter { System.currentTimeMillis()-it.lastModified()>24*60*60*1000 }?.forEach {it.delete()}
        return FileProvider.getUriForFile(context,"${context.packageName}.files",File.createTempFile("label-",".jpg",dir))
    }
    fun share(context:Context,scan:Scan) {
        val bitmap=Bitmap.createBitmap(1080,1500,Bitmap.Config.ARGB_8888)
        val canvas=Canvas(bitmap)
        canvas.drawColor(Color.rgb(245,247,250))
        val paint=Paint(Paint.ANTI_ALIAS_FLAG)
        fun text(value:String,y:Float,size:Float=32f,bold:Boolean=false,color:Int=Color.rgb(26,31,36)) {
            paint.textSize=size;paint.color=color;paint.typeface=if(bold) Typeface.create("sans-serif",Typeface.BOLD) else Typeface.create("sans-serif",Typeface.NORMAL)
            canvas.drawText(value,70f,y,paint)
        }
        fun wrap(value:String,start:Float,size:Float=32f,maxLines:Int=8):Float {
            paint.textSize=size
            var y=start; var line=""; var count=0
            for(word in value.split(Regex("\\s+"))) {
                if(paint.measureText("$line $word")>930 && line.isNotEmpty()) {
                    text(line,y,size);y+=size*1.5f;line="";count++
                    if(count>=maxLines-1) {text("… Consulta el análisis completo en la app.",y,size);return y+size*1.5f}
                }
                line=if(line.isBlank()) word else "$line $word"
            }
            if(line.isNotEmpty()) {text(line,y,size);y+=size*1.5f}
            return y
        }
        paint.color=Color.rgb(31,138,112);canvas.drawRect(0f,0f,1080f,160f,paint)
        text("lookupsafe",105f,52f,true,Color.WHITE)
        var y=wrap(scan.productName,240f,46f,3)+30
        text("LECTURA DE ETIQUETA",y,26f,true);y+=60
        y=wrap(scan.analysis.summary,y,34f,5)+25
        text("Menciones encontradas",y,32f,true);y+=55
        y=wrap(scan.analysis.allergens.joinToString(", "){it.name}.ifBlank {"Sin coincidencias en el catálogo limitado"},y,30f,4)+30
        text("Sin puntuación de seguridad",y,30f,true);y+=55
        wrap(scan.analysis.notice,y,27f,8)
        text("Revisa la etiqueta completa del producto",1390f,26f)
        text("${scan.createdAt.take(10)} · Verifica siempre el envase",1440f,26f)
        val file=File(directory(context),"lookupsafe-${scan.id}.png")
        file.outputStream().use { bitmap.compress(Bitmap.CompressFormat.PNG,100,it) };bitmap.recycle()
        val uri=FileProvider.getUriForFile(context,"${context.packageName}.files",file)
        context.startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
            type="image/png";putExtra(Intent.EXTRA_STREAM,uri);addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            clipData=android.content.ClipData.newRawUri("lookupsafe",uri)
        },"Compartir análisis"))
    }
}
