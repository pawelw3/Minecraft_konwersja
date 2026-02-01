package mapcleaner

/**
 * Kodowanie/dekodowanie bloków w formacie 1.7.10
 * Obsługuje: Blocks (4096 bajtów), Add (2048 bajtów nibble), Data (2048 bajtów nibble)
 */
object BlockCodec {
    
    /**
     * Pobiera nibble (4 bity) z tablicy bajtów
     */
    fun getNibble(array: ByteArray, index: Int): Int {
        val i = index shr 1
        val b = array[i].toInt() and 0xFF
        return if ((index and 1) == 0) (b and 0x0F) else ((b shr 4) and 0x0F)
    }
    
    /**
     * Ustawia nibble (4 bity) w tablicy bajtów
     */
    fun setNibble(array: ByteArray, index: Int, value: Int) {
        val i = index shr 1
        val b = array[i].toInt() and 0xFF
        val v = value and 0x0F
        val out = if ((index and 1) == 0) {
            ((b and 0xF0) or v)
        } else {
            ((b and 0x0F) or (v shl 4))
        }
        array[i] = out.toByte()
    }
    
    /**
     * Oblicza indeks w tablicy sekcji dla danego x, y, z (wszystkie 0-15)
     * Format: index = (y * 16 + z) * 16 + x
     */
    fun blockIndex(x: Int, y: Int, z: Int): Int {
        return (y * 16 + z) * 16 + x
    }
    
    /**
     * Odczytuje pełne ID bloku (12 bitów: low 8 z Blocks, high 4 z Add)
     */
    fun readFullId(blocks: ByteArray, add: ByteArray?, index: Int): Int {
        val low = blocks[index].toInt() and 0xFF
        val high = if (add == null) 0 else getNibble(add, index)
        return low or (high shl 8)
    }
    
    /**
     * Zapisuje pełne ID bloku i metadata
     * @return Zaktualizowana lub nowa tablica Add (jeśli high != 0)
     */
    fun writeFullId(
        blocks: ByteArray,
        add: ByteArray?,
        data: ByteArray,
        index: Int,
        fullId: Int,
        meta: Int = 0
    ): ByteArray? {
        // Zapisz low byte do Blocks
        blocks[index] = (fullId and 0xFF).toByte()
        
        // Zapisz high nibble do Add (jeśli potrzeba)
        val high = (fullId ushr 8) and 0x0F
        var newAdd = add
        
        if (high != 0) {
            if (newAdd == null) {
                newAdd = ByteArray(2048)
            }
            setNibble(newAdd, index, high)
        } else if (newAdd != null) {
            // Wyzeruj nibble jeśli high = 0
            setNibble(newAdd, index, 0)
        }
        
        // Zapisz metadata do Data
        setNibble(data, index, meta and 0x0F)
        
        return newAdd
    }
    
    /**
     * Odczytuje metadata bloku z Data
     */
    fun readMeta(data: ByteArray, index: Int): Int {
        return getNibble(data, index)
    }
    
    /**
     * Tworzy nową sekcję chunka z zadanym Y
     */
    fun createSection(y: Int): SectionData {
        return SectionData(
            y = y,
            blocks = ByteArray(4096),
            add = null, // Tworzymy tylko gdy potrzeba
            data = ByteArray(2048),
            skyLight = ByteArray(2048) { 0xFF.toByte() },
            blockLight = ByteArray(2048)
        )
    }
    
    /**
     * Klasa przechowująca dane sekcji
     */
    data class SectionData(
        val y: Int,
        val blocks: ByteArray,
        var add: ByteArray?,
        val data: ByteArray,
        val skyLight: ByteArray,
        val blockLight: ByteArray
    ) {
        /**
         * Sprawdza czy sekcja zawiera jakiekolwiek bloki (nie-same powietrze)
         */
        fun isEmpty(): Boolean {
            return blocks.all { it == 0.toByte() } && (add == null || add!!.all { it == 0.toByte() })
        }
        
        /**
         * Sprawdza czy sekcja używa Add (ma bloki >= 256)
         */
        fun usesAdd(): Boolean {
            return add != null && add!!.any { it != 0.toByte() }
        }
        
        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (other !is SectionData) return false
            
            return y == other.y &&
                   blocks.contentEquals(other.blocks) &&
                   add?.contentEquals(other.add ?: ByteArray(0)) == true &&
                   data.contentEquals(other.data) &&
                   skyLight.contentEquals(other.skyLight) &&
                   blockLight.contentEquals(other.blockLight)
        }
        
        override fun hashCode(): Int {
            var result = y
            result = 31 * result + blocks.contentHashCode()
            result = 31 * result + (add?.contentHashCode() ?: 0)
            result = 31 * result + data.contentHashCode()
            result = 31 * result + skyLight.contentHashCode()
            result = 31 * result + blockLight.contentHashCode()
            return result
        }
    }
}
