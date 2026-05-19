package dev.ftb.mods.ftbic.block.entity;

import dev.ftb.mods.ftbic.block.FTBICBlocks;
import java.util.function.Supplier;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.BlockEntityType.BlockEntitySupplier;
import net.minecraft.world.level.block.entity.BlockEntityType.Builder;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;

public interface FTBICBlockEntities {
   DeferredRegister<BlockEntityType<?>> REGISTRY = DeferredRegister.create(ForgeRegistries.BLOCK_ENTITIES, "ftbic");
   Supplier<BlockEntityType<?>> IRON_FURNACE = register("iron_furnace", IronFurnaceBlockEntity::new, FTBICBlocks.IRON_FURNACE);

   static Supplier<BlockEntityType<?>> register(String id, BlockEntitySupplier<?> supplier, Supplier<Block> block) {
      return REGISTRY.register(id, () -> Builder.m_155273_(supplier, new Block[]{block.get()}).m_58966_(null));
   }
}
