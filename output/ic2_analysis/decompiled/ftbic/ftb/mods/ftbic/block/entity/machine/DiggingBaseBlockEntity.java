package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBIC;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.block.FTBICBlocks;
import dev.ftb.mods.ftbic.net.MoveLaserMessage;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.util.FTBChunksIntegration;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.BlockPos.MutableBlockPos;
import net.minecraft.core.Direction.Axis;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.Nullable;

public class DiggingBaseBlockEntity extends BasicMachineBlockEntity {
   private static final int INVALID_Y = -10000;
   public boolean paused = false;
   public long tick = 0L;
   public float laserX = 0.5F;
   public int laserY = -10000;
   public float laserZ = 0.5F;
   public int offsetX = 1;
   public int offsetZ = -2;
   public int sizeX = 5;
   public int sizeZ = 5;
   public int skippedBlocks = 0;
   public float prevLaserX = 0.5F;
   public float prevLaserZ = 0.5F;
   public float moveLaserX = 0.5F;
   public int moveLaserY = 0;
   public float moveLaserZ = 0.5F;
   public long diggingMineTicks;
   public long diggingMoveTicks;

   public DiggingBaseBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128350_("LaserX", this.laserX);
      tag.m_128405_("LaserY", this.laserY);
      tag.m_128350_("LaserZ", this.laserZ);
      tag.m_128379_("Paused", this.paused);
      tag.m_128356_("Tick", this.tick);
      tag.m_128344_("OffsetX", (byte)this.offsetX);
      tag.m_128344_("OffsetZ", (byte)this.offsetZ);
      tag.m_128344_("SizeX", (byte)this.sizeX);
      tag.m_128344_("SizeZ", (byte)this.sizeZ);
      if (this.skippedBlocks > 0) {
         tag.m_128376_("SkippedBlocks", (short)this.skippedBlocks);
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.laserX = tag.m_128457_("LaserX");
      this.laserY = tag.m_128451_("LaserY");
      this.laserZ = tag.m_128457_("LaserZ");
      this.paused = tag.m_128471_("Paused");
      this.tick = tag.m_128454_("Tick");
      this.offsetX = tag.m_128445_("OffsetX");
      this.offsetZ = tag.m_128445_("OffsetZ");
      this.sizeX = Mth.m_14045_(tag.m_128445_("SizeX"), 1, 64);
      this.sizeZ = Mth.m_14045_(tag.m_128445_("SizeZ"), 1, 64);
      this.skippedBlocks = tag.m_128448_("SkippedBlocks");
   }

   @Override
   public void writeNetData(CompoundTag tag) {
      super.writeNetData(tag);
      tag.m_128350_("LaserX", this.laserX);
      tag.m_128405_("LaserY", this.laserY);
      tag.m_128350_("LaserZ", this.laserZ);
      tag.m_128379_("Paused", this.paused);
      tag.m_128356_("Tick", this.tick);
      tag.m_128344_("OffsetX", (byte)this.offsetX);
      tag.m_128344_("OffsetZ", (byte)this.offsetZ);
      tag.m_128344_("SizeX", (byte)this.sizeX);
      tag.m_128344_("SizeZ", (byte)this.sizeZ);
      tag.m_128347_("Speed", this.progressSpeed);
   }

   @Override
   public void readNetData(CompoundTag tag) {
      super.readNetData(tag);
      this.prevLaserX = this.moveLaserX = this.laserX = tag.m_128457_("LaserX");
      this.moveLaserY = this.laserY = tag.m_128451_("LaserY");
      this.prevLaserZ = this.moveLaserZ = this.laserZ = tag.m_128457_("LaserZ");
      this.paused = tag.m_128471_("Paused");
      this.tick = tag.m_128454_("Tick");
      this.offsetX = tag.m_128445_("OffsetX");
      this.offsetZ = tag.m_128445_("OffsetZ");
      this.sizeX = tag.m_128445_("SizeX");
      this.sizeZ = tag.m_128445_("SizeZ");
   }

   @Override
   public void handleProcessing() {
      this.active = !this.paused;
      if (this.f_58857_ != null && this.f_58857_.m_5776_()) {
         this.prevLaserX = this.laserX;
         this.prevLaserZ = this.laserZ;
         this.laserX = this.moveLaserX;
         this.laserY = this.moveLaserY;
         this.laserZ = this.moveLaserZ;
         if (!this.paused) {
            double x = (double)((float)this.f_58858_.m_123341_() + this.laserX);
            double minY = (double)this.laserY + 0.5;
            double maxY = (double)this.f_58858_.m_123342_() + 0.5;
            double z = (double)((float)this.f_58858_.m_123343_() + this.laserZ);
            FTBIC.PROXY.playLaserSound(this.f_58857_.m_46467_(), x, minY, maxY, z);
         }
      }

      if (!this.paused && this.f_58857_ != null && !this.f_58857_.m_5776_()) {
         if (!(this.energy >= this.energyUse)) {
            return;
         }

         this.energy = this.energy - this.energyUse;
         int var14 = Math.max((int)((double)this.diggingMineTicks / this.progressSpeed), 1);
         int moveTicks = Math.max((int)((double)this.diggingMoveTicks / this.progressSpeed), 1);
         int var15 = var14 + moveTicks;
         int ltick = (int)(this.tick % (long)var15);
         if (ltick <= moveTicks) {
            long s = (long)this.sizeX * (long)this.sizeZ * 2L;
            int lpos0 = (int)((this.tick / (long)var15 - 1L) % s);
            int lpos1 = (int)(this.tick / (long)var15 % s);
            if (lpos0 < 0) {
               lpos0 = (int)((long)lpos0 + s);
            }

            if ((long)lpos0 >= s / 2L) {
               lpos0 = (int)(s - (long)lpos0 - 1L);
            }

            if ((long)lpos1 >= s / 2L) {
               lpos1 = (int)(s - (long)lpos1 - 1L);
            }

            int row0 = lpos0 / this.sizeX;
            int col0 = row0 % 2 == 0 ? lpos0 % this.sizeX : this.sizeX - 1 - lpos0 % this.sizeX;
            int row1 = lpos1 / this.sizeX;
            int col1 = row1 % 2 == 0 ? lpos1 % this.sizeX : this.sizeX - 1 - lpos1 % this.sizeX;
            float lerp = (float)ltick / (float)moveTicks;
            this.laserX = (float)this.offsetX + Mth.m_14179_(lerp, (float)col0, (float)col1) + 0.5F;
            this.laserZ = (float)this.offsetZ + Mth.m_14179_(lerp, (float)row0, (float)row1) + 0.5F;
            this.laserY = this.getY(this.f_58858_.m_123341_() + Mth.m_14143_(this.laserX), this.f_58858_.m_123343_() + Mth.m_14143_(this.laserZ));
            this.sendLaserMove();
         }

         if (ltick == var15 - 1) {
            this.laserY = this.getY(this.f_58858_.m_123341_() + Mth.m_14143_(this.laserX), this.f_58858_.m_123343_() + Mth.m_14143_(this.laserZ));
            if (this.laserY == -10000) {
               this.skippedBlocks++;
               if (this.skippedBlocks >= this.sizeX * this.sizeZ * 2) {
                  this.paused = true;
                  this.skippedBlocks = 0;
                  this.syncBlock();
               }
            } else {
               BlockPos miningPos = new BlockPos(
                  (double)((float)this.f_58858_.m_123341_() + this.laserX), (double)this.laserY, (double)((float)this.f_58858_.m_123343_() + this.laserZ)
               );
               BlockState state = this.f_58857_.m_8055_(miningPos);
               this.skippedBlocks = 0;
               if (!this.f_58857_.m_5776_()) {
                  this.f_58857_.m_46473_().m_6180_("ftbic_" + this.electricBlockInstance.id);
                  double lx = (double)((float)this.f_58858_.m_123341_() + this.laserX);
                  double ly = (double)this.laserY + 0.5;
                  double lz = (double)((float)this.f_58858_.m_123343_() + this.laserZ);
                  this.digBlock(state, miningPos, lx, ly, lz);
                  this.f_58857_.m_46473_().m_7238_();
                  if (this.paused) {
                     this.syncBlock();
                  }
               }
            }
         }

         this.tick++;
      }
   }

   public boolean isValidBlock(BlockState state, BlockPos pos) {
      return false;
   }

   public void digBlock(BlockState state, BlockPos miningPos, double lx, double ly, double lz) {
   }

   private int getY(int x, int z) {
      MutableBlockPos pos = new MutableBlockPos(x, 0, z);
      if (this.f_58857_ instanceof ServerLevel && FTBChunksIntegration.instance.isProtected((ServerLevel)this.f_58857_, pos, this.placerId)) {
         return -10000;
      } else {
         for (int y = this.f_58858_.m_123342_(); y >= this.f_58857_.m_141937_(); y--) {
            pos.m_142448_(y);
            if (this.f_58857_.m_46749_(pos)) {
               BlockState state = this.f_58857_.m_8055_(pos);
               if (state.m_60734_() != Blocks.f_50752_ && state.m_60734_() != FTBICBlocks.EXFLUID.get() && !state.m_60795_() && this.isValidBlock(state, pos)) {
                  return y;
               }
            }
         }

         return -10000;
      }
   }

   public AABB getRenderBoundingBox() {
      return INFINITE_EXTENT_AABB;
   }

   @Override
   public boolean savePlacer() {
      return true;
   }

   public void resize() {
      Block landmark = (Block)FTBICBlocks.LANDMARK.get();
      Direction front = this.getFacing(Direction.NORTH);
      Direction back = front.m_122424_();
      Direction left = front.m_122427_();
      Direction right = front.m_122428_();
      int offBack = 6;
      int offLeft = 3;
      int offRight = 3;

      for (int i = 2; i <= 64; i++) {
         BlockState state = this.f_58857_.m_8055_(this.f_58858_.m_5484_(back, i));
         if (state.m_60734_() == landmark) {
            offBack = i;
            break;
         }
      }

      for (int ix = 1; ix <= 64; ix++) {
         BlockState state = this.f_58857_.m_8055_(this.f_58858_.m_5484_(left, ix));
         if (state.m_60734_() == landmark) {
            offLeft = ix;
            break;
         }
      }

      for (int ixx = 1; ixx <= 64; ixx++) {
         BlockState state = this.f_58857_.m_8055_(this.f_58858_.m_5484_(right, ixx));
         if (state.m_60734_() == landmark) {
            offRight = ixx;
            break;
         }
      }

      offBack--;
      offLeft--;
      offRight--;
      if (back.m_122434_() == Axis.X) {
         this.sizeX = offBack;
         this.sizeZ = offLeft + offRight + 1;
         this.offsetX = back.m_122429_() == 1 ? 1 : -this.sizeX;
         this.offsetZ = -(back.m_122429_() == 1 ? offLeft : offRight);
      } else if (back.m_122434_() == Axis.Z) {
         this.sizeX = offLeft + offRight + 1;
         this.sizeZ = offBack;
         this.offsetX = -(back.m_122431_() == 1 ? offRight : offLeft);
         this.offsetZ = back.m_122431_() == 1 ? 1 : -this.sizeZ;
      }

      this.syncBlock();
   }

   @Override
   public void onPlacedBy(@Nullable LivingEntity entity, ItemStack stack) {
      super.onPlacedBy(entity, stack);
      Direction dir = this.getFacing(Direction.NORTH).m_122424_();
      this.laserX = (float)dir.m_122429_() + 0.5F;
      this.laserZ = (float)dir.m_122431_() + 0.5F;
      if (this.f_58857_.m_7702_(this.f_58858_.m_7495_()) instanceof DiggingBaseBlockEntity q) {
         this.offsetX = q.offsetX;
         this.offsetZ = q.offsetZ;
         this.sizeX = q.sizeX;
         this.sizeZ = q.sizeZ;
         this.syncBlock();
      } else {
         this.resize();
      }
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addBoolean(SyncedData.PAUSED, () -> this.paused);
   }

   public void moveLaser(float x, int y, float z) {
      this.moveLaserX = x;
      this.moveLaserY = y;
      this.moveLaserZ = z;
   }

   private void sendLaserMove() {
      LevelChunk chunk = this.f_58857_ == null ? null : this.f_58857_.m_46745_(this.f_58858_);
      if (chunk != null) {
         new MoveLaserMessage(this.f_58858_, this.laserX, this.laserY, this.laserZ).sendToChunkListeners(chunk);
      }
   }

   public float[] getLaserColor() {
      return new float[]{1.0F, 1.0F, 1.0F};
   }
}
